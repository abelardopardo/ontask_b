import json
import os
import requests
import logging
import environ

# Setting up logging
logging.basicConfig(level=logging.INFO)
env = environ.Env()

config = {
    'canvas_base_url': env("CANVAS_BASE_URL"),
    'canvas_api_token': env("CANVAS_API_TOKEN"),
    'ontask_base_url': env("ONTASK_BASE_URL"),
    'ontask_api_token': env("ONTASK_API_TOKEN")
}

print("CANVAS_BASE_URL", env("CANVAS_BASE_URL", default=""))
print("CANVAS_API_TOKEN", env("CANVAS_API_TOKEN", default=""))
print("ONTASK_BASE_URL", env("ONTASK_BASE_URL", default=""))
print("ONTASK_API_TOKEN", env("ONTASK_API_TOKEN", default=""))

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