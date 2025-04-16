import openai 
import requests
from config import settings

async def infer(
    api_key,
    base_url,
    model_name,
    messages
):
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=5000,
    )
    return response


    # for batch in response:
    #     if batch.choices[0].delta.content:
    #         yield batch.choices[0].delta.content

    return response.choices[0].message.content

def generate_chat_completion_openai(
        messages: list, 
    ):

    # headers = {
    #     'Content-Type': 'application/json',
    # }

    json_data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages
    }

    response = requests.post(
        'http://gpt-nha-lam:8080/v1/chat/completions', 
        # headers=headers, 
        json=json_data
    )
    print(response.text)
    return response.json()


def generate_chat_completion_gemini(
    messages,
):
    client = openai.OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
    )
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=messages,
        temperature=0.7,
        max_tokens=5000,
    )
    return response
