import requests
from config import settings
def chunk_text_by_chars(text: str, max_chars: int = 1990) -> list[str]:
    chunks = []
    while len(text) > max_chars:
        # Tìm dấu xuống dòng gần nhất hoặc khoảng trắng gần nhất để cắt
        split_index = text.rfind("\n", 0, max_chars)
        if split_index == -1:
            split_index = text.rfind(" ", 0, max_chars)
        if split_index == -1:
            split_index = max_chars

        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()

    if text:
        chunks.append(text)
    return chunks

def send_discord_notification(prompt:str, content: str):
    webhook_url = settings.discord_webhook_url
    chunks = chunk_text_by_chars(content)

    data = {"content": f"""
QUESTION : {prompt}
```ansi
[2;31mSYSTEM PROMPT:[0m
```
"""}
    response = requests.post(webhook_url, json=data)

    for chunk in chunks:
        print(f"🧩 Sending chunk with {len(chunk)} chars")
        data = {"content": chunk}
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("✅ Sent successfully!")
        else:
            print(f"❌ Failed to send: {response.status_code}, {response.text}")

def send_discord_fc_notification(prompt:str, function_name, function_args, result):
    webhook_url = settings.discord_fc_webhook_url
    # chunks = chunk_text_by_chars(content)

    data = {"content": f"""
QUESTION : {prompt}
```ansi
[2;31mFUNCTION CALLING DETAILS:[0m
```
"""}
    response = requests.post(webhook_url, json=data)

    # for chunk in chunks:
    # print(f"🧩 Sending chunk with {len(chunk)} chars")
    data = {"content": f"""
FUNCTION NAME : {function_name} 
FUNCTION ARGS: {function_args}
RESULT: 
```
{result}
```
"""}
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("✅ Sent successfully!")
    else:
        print(f"❌ Failed to send: {response.status_code}, {response.text}")
    

