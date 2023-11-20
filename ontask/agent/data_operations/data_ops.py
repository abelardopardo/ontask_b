import json
import os
import requests
import logging
import pandas as pd
import functools
import environ
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
# Fetch quiz statistics   
def fetch_canvas_data_quiz_stats(course_id, quiz_id):
    headers = {
        "Authorization": f"Bearer {config['canvas_api_token']}",
    }
    endpoint = f"{config['canvas_base_url']}/api/v1/courses/{course_id}/quizzes/{quiz_id}/statistics"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        try:
            res = []
            quizStat = response.json()
            for qstat in quizStat['quiz_statistics']:
                questions = qstat['question_statistics']
                for ques in questions:
                    user_answers = {}
                    for ans in ques['answers']:
                        for user_name in ans['user_names']:
                            if user_name not in user_answers:
                                user_answers[user_name] = {
                                    "user": user_name,
                                    "question": ques['question_text'].strip(),
                                    "answers": []
                                }
                            user_answers[user_name]['answers'].append(ans['text'])
                    # Flatten the answers and add to the result
                    for user_data in user_answers.values():
                        user_data['answers'] = ", ".join(user_data['answers'])
                        res.append(user_data)    
            # Create DataFrame and return
            quiz_stats = pd.DataFrame(res)
            return quiz_stats
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {response.text}")
            return pd.DataFrame()
    else:
        logging.error(f"Error fetching Canvas data: {response.status_code}, {response.text}")
        return pd.DataFrame()
    
def update_ontask_table(new_data, wid):
    src_df = new_data.to_dict(orient='records')
    data_payload = {
        "how": "left",  # or "right", "inner", "outer", etc.
        "left_on": ["user", "id"],
        "right_on": ["user","id"],
        "src_df": src_df
    }
    headers = {
        "Authorization": f"Token {config['ontask_api_token']}"
    }
    endpoint = f"{config ['ontask_base_url']}/table/{wid}/pmerge/"
    response = requests.put(endpoint, headers=headers, json=data_payload)
    if response.status_code == 200:  # Check if this is the correct success status code
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