import openai 
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