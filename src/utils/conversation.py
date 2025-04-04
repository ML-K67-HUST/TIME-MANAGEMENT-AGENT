import requests
from config import settings

def get_history(userid:int, token:str):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization':f'bearer {token}'
    }

    json_data = {
        'userid': userid,
    }

    response = requests.post(f'{settings.backend_url}/conversation/query', headers=headers, json=json_data)   
    return response.json()

def extract_chat_history(api_response: dict, limit: int = 10):
    history_records = api_response.get("history", [])
    if not history_records:
        return []

    chat_history = history_records[0].get("history", [])

    formatted_history = [
        {"user": msg["user"], "assistant": msg["assistant"]}
        for msg in chat_history
    ]

    return formatted_history[-limit:] 

def update_history(userid: int, token:str, user: str, assistant:str):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'bearer {token}'
    }

    json_data = {
        'userid': userid,
        'history': {
            'user': user,
            'assistant': assistant
        },
    }

    response = requests.post(f'{settings.backend_url}/conversation/update', headers=headers, json=json_data)
    return response.json()