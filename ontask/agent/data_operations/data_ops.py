import json
import os
import requests
import logging
import pandas as pd
from colorama import Fore

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Read configuration from JSON file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

with open(CONFIG_PATH, 'r') as file:
    config = json.load(file)

def fetch_canvas_data(course_id, quiz_id):
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

def fetch_ontask_data():
    headers = {
        "accept": "application/json" ,
        "X-CSRFToken": "BD0VkMLFKLrpOnwuGC8qjgG1LAGfGjt4A1vtJ4vMpJRwhASntwaebIo01VzSl5dI",
        "Authorization": f"Bearer {config['ontask_api_token']}"
    }
    endpoint = f"{config['ontask_base_url']}/table"
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        try:
            return pd.DataFrame(response.json())
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {response.text}")
            return pd.DataFrame()
    else:
        logging.error(f"Error fetching OnTask data: {response.status_code}, {response.text}")
        return pd.DataFrame()


def update_ontask_table(new_data, wid):
    headers = {
        "accept": "application/json" ,
        "X-CSRFToken": "",
        "Authorization": f"Bearer {config['ontask_api_token']}"
    }
    endpoint = f"{config['ontask_base_url']}/table/{wid}/merge/"
    data_payload = new_data.to_dict(orient="records")
    response = requests.post(endpoint, headers=headers, json=data_payload)
    
    if response.status_code == 201:
        logging.info("Successfully updated OnTask table.")
        return True
    else:
        logging.error(f"Failed to update OnTask table: {response.text}")
        return False

def data_has_changes(canvas_data, ontask_data):
    if canvas_data.empty and ontask_data.empty:
        return False
    if canvas_data.empty or ontask_data.empty:
        return True
    return not canvas_data.equals(ontask_data)