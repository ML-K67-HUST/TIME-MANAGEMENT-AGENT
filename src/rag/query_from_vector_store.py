import requests
from config import settings
def query_for_about_us(prompt):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    params = {
        'vector_store': 'milvus',
    }

    json_data = {
        'query_texts': [
            prompt,
        ],
        'n_results': 2,
        'where': {},
        'where_document': {},
        'rerank': False,
    }

    response = requests.post(
        f'{settings.vector_store_url}/collections/about_us/query',
        params=params,
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        print("ABOUT US OK 🚀")
        data = response.json()
        retrieved_data = ""
        for datum in data:
            retrieved_data += datum["metadata"]["content"] + "\n\n"
        print(retrieved_data)
        return retrieved_data
    else:
        return "Error happened when retrieving ABOUT-US data"
