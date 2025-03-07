import asyncio
from googlesearch import search
from constants.prompt_library import GG_SEARCH_SYSTEM_PROMPT
import trafilatura
from core.chat import generate_chat_completions

async def fetch_and_extract(url):
    downloaded = trafilatura.fetch_url(url)
    return trafilatura.extract(downloaded) if downloaded else None

async def process_post(post):
    extracted = await fetch_and_extract(post["url"])
    if not extracted:
        return None  

    answer = await generate_chat_completions(
        prompt=extracted,
        system_prompt=GG_SEARCH_SYSTEM_PROMPT
    )

    return {
        "title": post["title"],
        "url": post["url"],
        "detail": extracted,
        "answer": answer
    }

async def get_google_search(query: str, max_num_results=5):
    """Tìm kiếm Google và xử lý song song"""
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