import openai 
import requests
from config import settings

async def generate_chat_completions( prompt: str,system_prompt : str):
    client = openai.OpenAI(
        api_key=settings.together_api_key,
        base_url="https://api.together.xyz/v1",
    )

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    messages.append({
        "role":"user",
        "content": prompt,
    })


    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages,
        # stream=True,
    )


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