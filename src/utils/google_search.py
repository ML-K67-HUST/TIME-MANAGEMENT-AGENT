import asyncio
from googlesearch import search
from constants.prompt_library import GG_SEARCH_SYSTEM_PROMPT
import trafilatura
from utils.chat import infer
import openai
from config import settings
from bs4 import BeautifulSoup
import time
import requests
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
        api_key=settings.gemini_vision_api_key,
        base_url=settings.gemini_base_url,
        messages=messages,
        model_name="gemini-2.0-flash"
    )

    return {
        "title": post["title"],
        "url": post["url"],
        "detail": extracted,
        "answer": answer.choices[0].message.content
    }

async def get_google_search(query: str, max_num_results=2):
    search_results = [
        {"title": post.title, "url": post.url}
        for post in search(query, num_results=max_num_results, advanced=True)
    ]

    tasks = [process_post(post) for post in search_results]
    results = await asyncio.gather(*tasks)

    return [r for r in results if r]

async def get_vnexpress(url:str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    results = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')

        for idx, article in enumerate(articles, 1):
            a_tag = article.find('a')
            if a_tag and a_tag.has_attr('href'):
                article_url = a_tag['href']
                print(f"\n📰 Crawling Article {idx}: {article_url}")

                # Truy cập từng bài báo
                article_resp = requests.get(article_url, headers=headers)
                if article_resp.status_code == 200:
                    article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                    sidebar_div = article_soup.find("div", class_="sidebar-1")

                    if sidebar_div:
                        header = ""
                        content_parts = []
                        date = ""

                        # Lấy h1
                        h1_tag = sidebar_div.find("h1")
                        if h1_tag:
                            header = h1_tag.get_text(strip=True)

                        # Lấy p
                        p_tags = sidebar_div.find_all("p")
                        for p in p_tags:
                            text = p.get_text(strip=True)
                            if text:
                                content_parts.append(text)

                        # Lấy span class="date"
                        span_tag = sidebar_div.find("span", class_="date")
                        if span_tag:
                            date = span_tag.get_text(strip=True)

                        # Gộp thành dict
                        article_data = {
                            "header": header,
                            "content": "\n".join(content_parts),
                            "date": date
                        }
                        results.append(article_data)
                    else:
                        print("⚠️ Không tìm thấy div.sidebar-1")
                else:
                    print(f"❌ Lỗi khi truy cập bài báo, status code: {article_resp.status_code}")

                time.sleep(1)  # Sleep 1s giữa mỗi bài để tránh bị chặn IP
    else:
        print(f"❌ Lỗi khi tải trang chủ AI, status code: {response.status_code}")

    return results



if __name__ == "__main__":
    print(asyncio.run(get_google_search(
        query = "quản lý thời gian",
        max_num_results=5
    )))