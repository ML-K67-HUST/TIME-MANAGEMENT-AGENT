import requests

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

json_data = {
    'input': 'hi',
}

response = requests.post('http://localhost:8002/v1/embeddings', headers=headers, json=json_data)


print(response.json()["data"][0]["embedding"])