import json
import os
import requests
import logging
from colorama import Fore
import pandas as pd

# Setting up logging
logging.basicConfig(level=logging.INFO)

# Load config.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

with open(CONFIG_PATH, 'r') as file:
    config = json.load(file)

    
def fetch_canvas_data():
    headers = {
        "Authorization": f"Bearer {config['canvas_api_token']}"
    }
    endpoint = f"{config['canvas_base_url']}/api/v1/courses/396/quizzes/377/submissions"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error fetching courses: {response.text}")
        return []

def data_has_changes(canvas_data, ontask_data):
    # Check if either DataFrame is empty
    if canvas_data.empty and ontask_data.empty:
        return False  # No changes if both are empty
    
    if canvas_data.empty or ontask_data.empty:
        return True  # One is empty, and the other is not, so they can't be equal
    
    # If neither are empty, then compare them based on your criteria
    return not canvas_data.equals(ontask_data)


# # Merging data from Canvas to OnTask workflow
def merge_data_to_ontask(df, wid):
    headers = {
        "authorization": f"Basic 96ceb3b04c66be6b1ba60aca9e7ac09fcc153509",
        "accept": "application/json",
        "X-CSRFToken": f"{config['ontask_api_token']}"
    }
    endpoint = f"{config['ontask_base_url']}/table/{wid}/merge"  
    
    data_payload = df.to_dict()  # Assuming df is a DataFrame
    
    response = requests.put(endpoint, headers=headers, json=data_payload)
    if response.status_code == 200:  
        logging.info("Successfully merged data to OnTask.")
        return True
    else:
        logging.error(f"Failed to merge data to OnTask. Status Code: {response.status_code}")
        logging.error(response.text)
        return False