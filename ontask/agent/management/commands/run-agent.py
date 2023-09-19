from django.core.management.base import BaseCommand
import requests
import json

class Command(BaseCommand):
    help = 'Run the agent to authenticate with Canvas and OnTask platforms'

    def handle(self, *args, **kwargs):
        with open('config.json', 'r') as file:
            config = json.load(file)

        def authenticate_canvas():
            headers = {
                "Authorization": f"Bearer {config['canvas_api_token']}"
            }
            endpoint = f"{config['canvas_base_url']}/api/v1/accounts/self"
            response = requests.get(endpoint, headers=headers)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('Authenticated with Canvas successfully!'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to authenticate with Canvas. Status Code: {response.status_code}'))
                self.stdout.write(self.style.ERROR(response.text))

        def authenticate_ontask():
            headers = {
                "Authorization": f"Bearer {config['ontask_api_token']}"
            }
            endpoint = f"{config['ontask_base_url']}/api/v1/"
            response = requests.get(endpoint, headers=headers)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('Authenticated with OnTask successfully!'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to authenticate with OnTask. Status Code: {response.status_code}'))
                self.stdout.write(self.style.ERROR(response.text))

        # Execute the methods:
        authenticate_canvas()
        authenticate_ontask()