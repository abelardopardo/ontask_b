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
from datetime import datetime

logging.basicConfig(level=logging.INFO)
env = environ.Env()

config = {
    'canvas_base_url': env("CANVAS_BASE_URL"),
    'canvas_api_token': env("CANVAS_API_TOKEN"),
    'ontask_base_url': env("ONTASK_BASE_URL"),
    'ontask_api_token': env("ONTASK_API_TOKEN")
}

def parse_date(date_string):
    if isinstance(date_string, str):
        return datetime.fromisoformat(date_string.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    return None


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
        "Authorization": f"Bearer {config['canvas_api_token']}"
    }
    endpoint = f"{config['canvas_base_url']}/api/v1/courses/{course_id}/quizzes/{quiz_id}/statistics"
    response = requests.get(endpoint, headers=headers)

    if response.status_code != 200:
        logging.error(f"Error fetching Canvas data: {response.status_code}, {response.text}")
        return pd.DataFrame()

    # Fetch quiz submissions data
    df_submissions = fetch_canvas_data_submissions(course_id, quiz_id)

    quizStat = response.json()
    points_possible = quizStat['quiz_statistics'][0]['points_possible']
    multiple_attempts_exist = quizStat['quiz_statistics'][0].get('multiple_attempts_exist', False)

    all_user_answers = []
    user_scores = {}
    for qstat in quizStat['quiz_statistics']:
        questions = qstat['question_statistics']
        for ques in questions:
            for ans in ques['answers']:
                correct_flag = ans['correct']
                for user_id, user_name in zip(ans['user_ids'], ans['user_names']):
                    all_user_answers.append({
                        "id": user_id,
                        "name": user_name,
                        "question_id": ques['id'],
                        "answer": ans['text']
                    })
                    if correct_flag:
                        user_scores.setdefault(user_id, 0)
                        user_scores[user_id] += points_possible / len(questions)  

    df_answers = pd.DataFrame(all_user_answers)

    df_pivoted = df_answers.pivot_table(index=['id', 'name'], 
                                        columns='question_id', 
                                        values='answer', 
                                        aggfunc=lambda x: ', '.join(x)).reset_index()

    question_cols = {col: f'Question {idx+1}' for idx, col in enumerate(df_pivoted.columns[2:])}
    df_pivoted.rename(columns=question_cols, inplace=True)

    df_pivoted['Total Score'] = df_pivoted['id'].map(user_scores).apply(lambda x: round(x, 1))

    # Consider 'multiple_attempts_exist' for attempts count
    if multiple_attempts_exist:
        df_pivoted['Attempts'] = df_pivoted['id'].map(df_submissions.groupby('user_id')['attempt'].max())
    else:
        df_pivoted['Attempts'] = 1  # Only one attempt allowed

    merged_df = pd.merge(df_pivoted, df_submissions[['user_id', 'started_at', 'finished_at']], 
                         left_on='id', right_on='user_id', how='left')

    merged_df.drop('user_id', axis=1, inplace=True)
    merged_df.rename(columns={'started_at': 'Start Time', 'finished_at': 'End Time'}, inplace=True)
    merged_df['Start Time'] = merged_df['Start Time'].apply(parse_date)
    merged_df['End Time'] = merged_df['End Time'].apply(parse_date)

    return merged_df

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
    response = requests.put(endpoint, headers=headers, json=data_payload)
    if response.status_code in [200, 201, 204]: 
        logging.info("Data merged successfully into OnTask")
        return True
    else:
        logging.error(f"Failed to merge OnTask table: {response.status_code}, {response.text}")
        return False


def fetch_ontask_data(wid):
    headers = {
        "Authorization": f"Token {config['ontask_api_token']}",
        "Content-Type": "application/json"
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