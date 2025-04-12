import openai
from constants.prompt_library import CLASSIFIER_PROMPT
from config import settings
import json 
import requests
import json
import re

def extract_json_from_response(response: str) -> dict:

    try:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = response.strip()
        
        return json.loads(json_str)
    
    except Exception as e:
        raise ValueError(f"Failed to parse JSON from response: {e}")


def classify_prompt(prompt: str) -> bool:
    # client = openai.OpenAI(
    #     api_key=settings.together_api_key,
    #     base_url="https://api.together.xyz/v1",
    # )
    try:
        client = openai.OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url
        )
        response = client.chat.completions.create(
            # model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
        
        answer = response.choices[0].message.content
        
        return extract_json_from_response(answer)
    except Exception as e:
        print("❌ Error happened for classifier: ",e)
        return {
            'about_us': False, 
            'domain_knowledge': False, 
            'task_management': False, 
            'function_calling': False
        }


def classify_modestus(prompt: str):

    headers = {
        'Content-Type': 'application/json',
        'moev-api-key': '2a2e45f4-5dda-484f-a8c5-ea03594230c9',
    }

    json_data = {
        'content': prompt,
        'request_id': '40119acc-bb9a-421b-8034-756be1535e00',
        'metrics': {
            'about_us': 'the message is asking about the business or who built it (e.g., "who are you", "what is this", "who made you")',
            'domain_knowledge': 'the message asks general knowledge questions (e.g., "what is machine learning", "what should I learn for AI")',
            'task_management': 'the message relates to productivity, scheduling, or performance (e.g., "how to be more productive", "how to focus better")',
        },
    }

    response = requests.post('https://api.modestus.ai/moderate_specialist_001', headers=headers, json=json_data)

    return response.json()