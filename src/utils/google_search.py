import asyncio
from googlesearch import search
from constants.prompt_library import GG_SEARCH_SYSTEM_PROMPT
import trafilatura
from utils.chat import infer
import openai
from config import settings
def classify_prompt(prompt: str) -> bool:
    client = openai.OpenAI(
        api_key=settings.together_api_key,
        base_url="https://api.together.xyz/v1",
    )
    
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[
            {"role": "system", "content": "You are an effective classifier, return `1` if you find the content is relate to productivity, else return `0`"},
            {"role": "user", "content": prompt},
        ]
    )
    
    answer = response.choices[0].message.content.strip().lower()
    return answer == "1"
async def fetch_and_extract(url):
    downloaded = trafilatura.fetch_url(url)
    return trafilatura.extract(downloaded) if downloaded else None

async def process_post(post):
    extracted = await fetch_and_extract(post["url"])
    if not extracted:
        return None  
    messages = [
        {
            "role":"system",
            "content":GG_SEARCH_SYSTEM_PROMPT
        },
        {
            "role":"user",
            "content":f"TITLE:{post['title']}\n\nCONTENT:{extracted}"[:5000]
        }
    ]
    answer = await infer(
        api_key=settings.together_api_key,
        base_url=settings.together_base_url,
        messages=messages,
        model_name="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    )

    return {
        "title": post["title"],
        "url": post["url"],
        "detail": extracted,
        "answer": answer
    }

async def get_google_search(query: str, max_num_results=2):
    search_results = [
        {"title": post.title, "url": post.url}
        for post in search(query, num_results=max_num_results, advanced=True)
    ]

    tasks = [process_post(post) for post in search_results]
    results = await asyncio.gather(*tasks)

    return [r for r in results if r]


if __name__ == "__main__":
    print(asyncio.run(get_google_search(
        query = "tips for time management",
        max_num_results=2
    )))