import json
import os
import requests
import logging
import environ
from colorama import Fore
import pandas as pd

from ontask.agent.canvas_api.c3l import C3L
# Setting up logging
logging.basicConfig(level=logging.INFO)

env = environ.Env()

class agent:
    def __init__(self):
        self.canvas_base_url  = env("CANVAS_BASE_URL" , default="")
        self.canvas_api_token = env("CANVAS_API_TOKEN", default="")
        self.ontask_base_url  = env("ONTASK_BASE_URL" , default="")
        self.ontask_api_token = env("ONTASK_API_TOKEN", default="")

        self.__base_path__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__c3l__ = C3L(
            self.canvas_base_url,
            self.canvas_api_token
        )

    def create_course(self):
        pass

    def get_quizes(self):
        pass


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