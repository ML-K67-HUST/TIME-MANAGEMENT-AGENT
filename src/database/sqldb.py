
import requests
def get_user_info(userid, token):
    url = f"http://app:5050/sqldb/users/{userid}"

    payload = {}
    headers = {
    'Authorization': f'bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()
    

def get_user_tasks(userid, token):
    url = f"http://app:5050/sqldb/tasks/{userid}"

    payload = {}
    headers = {
    'Authorization': f'bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()




