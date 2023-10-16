import json
import os
import requests
import logging

# Setting up logging
logging.basicConfig(level=logging.INFO)

# Load config.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

with open(CONFIG_PATH, 'r') as file:
    config = json.load(file)

def authenticate_canvas():
    headers = {
        "Authorization": f"Bearer {config['canvas_api_token']}"
    }
    endpoint = f"{config['canvas_base_url']}/api/v1/accounts/self"
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        logging.info("Authenticated with Canvas successfully!")
        return True
    else:
        logging.error(f"Failed to authenticate with Canvas. Status Code: {response.status_code}")
        logging.error(response.text)
        return False

def fetch_canvas_data():
    headers = {
        "Authorization": f"Bearer {config['canvas_api_token']}"
    }
    endpoint = f"{config['canvas_base_url']}/api/v1/courses/396/quizzes/374/submissions"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error fetching courses: {response.text}")
        return []

def update_ontask_table(new_data):
    headers = {
        "Authorization": f"Bearer {config['ontask_api_token']}"
    }
    endpoint = f"{config['ontask_base_url']}table/"  # Make sure to use the correct endpoint

    # Prepare data for posting
    # Depending on the OnTask API, you may need to format or transform new_data 
    # Here, I assume OnTask expects an array of courses, but adjust as needed
    data_payload = {
        "courses": new_data
    }

    response = requests.post(endpoint, headers=headers, json=data_payload)
    if response.status_code == 201:  # HTTP 201 typically indicates a successful POST request
        logging.info("Successfully posted data to OnTask.")
        return True
    else:
        logging.error(f"Failed to post data to OnTask. Status Code: {response.status_code}")
        logging.error(response.text)
        return False