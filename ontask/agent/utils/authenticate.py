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