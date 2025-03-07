import openai
from config import settings
from constants.prompt_library import SYSTEM_PROMPT

async def generate_chat_completions(prompt: str, history=[] , system_prompt=SYSTEM_PROMPT):
    client = openai.OpenAI(
        api_key=settings.together_api_key,
        base_url="https://api.together.xyz/v1",
    )
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    for message in history:
        messages.append({
            "role":"user",
            "content": message["user"]
        })
        messages.append({
            "role":"assistant",
            "content": message["assistant"]
        })

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
