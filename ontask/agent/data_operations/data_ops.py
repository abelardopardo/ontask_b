import json
import os
import requests
import logging
import pandas as pd
import functools
import environ
import re
import html
import base64
from io import BytesIO
from django.shortcuts import reverse


logging.basicConfig(level=logging.INFO)
env = environ.Env()

config = {
    'canvas_base_url': env("CANVAS_BASE_URL"),
    'canvas_api_token': env("CANVAS_API_TOKEN"),
    'ontask_base_url': env("ONTASK_BASE_URL"),
    'ontask_api_token': env("ONTASK_API_TOKEN")
}


def fetch_canvas_data_submissions(course_id, quiz_id):
    headers = {
        "Authorization": f"Bearer {config['canvas_api_token']}"
    }
    endpoint = f"{config['canvas_base_url']}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions"
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            return pd.DataFrame(data['quiz_submissions'])
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {response.text}")
            return pd.DataFrame()  
    else:
        logging.error(f"Error fetching Canvas data: {response.status_code}, {response.text}")
        return pd.DataFrame()
    
def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = html.unescape(text)
    text = text.replace('####', '')
    return text.strip()

def fetch_canvas_data_quiz_stats(course_id, quiz_id):
    headers = {
        "Authorization": f"Bearer {config['canvas_api_token']}",
    }
    endpoint = f"{config['canvas_base_url']}/api/v1/courses/{course_id}/quizzes/{quiz_id}/statistics"
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        try:
            all_user_answers = []
            quizStat = response.json()
            for qstat in quizStat['quiz_statistics']:
                questions = qstat['question_statistics']
                for ques in questions:
                    for ans in ques['answers']:
                        for user_id, user_name in zip(ans['user_ids'], ans['user_names']):
                            all_user_answers.append({
                                "id": user_id,
                                "name": user_name,
                                "question_id": ques['id'],
                                "answer": ans['text']
                            })
            
            # Create DataFrame from the collected answers
            df_answers = pd.DataFrame(all_user_answers)
            
            # Pivot the DataFrame to have separate columns for each question's answers
            df_pivoted = df_answers.pivot_table(index=['id', 'name'], 
                                                columns='question_id', 
                                                values='answer', 
                                                aggfunc=lambda x: ', '.join(x)).reset_index()
            
            # Rename the question columns to match OnTask format (e.g., 'Question 1', 'Question 2', etc.)
            question_cols = {col: f'Question {idx+1}' for idx, col in enumerate(df_pivoted.columns[2:])}
            df_pivoted.rename(columns=question_cols, inplace=True)

            return df_pivoted

        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {response.text}")
            return pd.DataFrame()
    else:
        logging.error(f"Error fetching Canvas data: {response.status_code}, {response.text}")
        return pd.DataFrame()

def dataframe_to_base64(df):
    # Use a BytesIO buffer instead of writing to disk
    buffer = BytesIO()
    # Convert DataFrame to a pickle byte stream and write to buffer
    df.to_pickle(buffer)
    # Seek to the start of the stream
    buffer.seek(0)
    # Base64 encode the byte stream
    b64_bytes = base64.b64encode(buffer.read())
    # Convert bytes to string
    b64_string = b64_bytes.decode()
    return b64_string

def update_ontask_table(new_data, wid):
    b64_string = dataframe_to_base64(new_data)
    data_payload = {
        "how": "outer",  # or "right", "inner", "outer", etc.
        "left_on": "id", # destination (OnTask)
        "right_on": "id", # source
        "src_df": b64_string # new dataframe ready to be merged
    }
    headers = {
        "Authorization": f"Token {config['ontask_api_token']}",
        "Content-Type": "application/json"
    }
    endpoint = f"{config ['ontask_base_url']}/table/{wid}/pmerge/"
    # reverse('table:api_pmerge', kwargs = {'wid': wid})
    response = requests.put(endpoint, headers=headers, json=data_payload)
    if response.status_code in [200, 201, 204]: 
        logging.info("Data merged successfully into OnTask")
        return True
    else:
        logging.error(f"Failed to merge OnTask table: {response.status_code}, {response.text}")
        return False


def fetch_ontask_data(wid):
    headers = {
        "accept": "application/json" ,
        "Authorization": f"Bearer {config['ontask_api_token']}"
    }
    endpoint = f"{config['ontask_base_url']}/table/{wid}/merge"
    response = requests.get(endpoint, headers=headers)

    logging.info(f"Request to {endpoint} with headers {headers} returned {response.status_code}")
    logging.error(f"Error fetching OnTask data: {response.status_code}, Response: {response.text}")
    if response.status_code == 200:
        try:
            return pd.DataFrame(response.json())
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {response.text}")
            return pd.DataFrame()
    else:
        logging.error(f"Error fetching OnTask data: {response.status_code}, {response.text}")
        return pd.DataFrame()


def data_has_changes(canvas_data, ontask_data):
    if canvas_data.empty and ontask_data.empty:
        return False
    if canvas_data.empty or ontask_data.empty:
        return True
    return not canvas_data.equals(ontask_data)