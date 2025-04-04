
import requests
from config import settings
def get_user_info(userid, token):
    url = f"{settings.backend_url}/sqldb/users/{userid}"

    payload = {}
    headers = {
    'Authorization': f'bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()
    

def get_user_tasks(userid, token):
    url = f"{settings.backend_url}/sqldb/tasks/{userid}"

    payload = {}
    headers = {
    'Authorization': f'bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()




