import json
import os
import requests
import logging
import environ

from ontask.agent.canvas_api.c3l import C3L
# Setting up logging
logging.basicConfig(level=logging.INFO)
env = environ.Env()
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