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
from datetime import datetime

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

def parse_date_get_timestamp(date_str):
    """
    Trả về tuple (datetime object, int timestamp) từ string ngày giờ.
    Nếu lỗi thì trả về (None, None)
    """
    try:
        # VD input: "Thứ ba, 29/4/2025, 10:53 (GMT+7)"
        parts = date_str.split(", ")
        if len(parts) < 3:
            return None, None
        # date_part = "29/4/2025"
        # time_part = "10:53"
        date_part = parts[1]
        time_part = parts[2].split(" ")[0]

        datetime_str = f"{date_part} {time_part}"  # "29/4/2025 10:53"
        dt = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M")
        timestamp = int(dt.timestamp())-25200
        return dt, timestamp
    except Exception as e:
        print(f"⚠️ Lỗi khi parse datetime: {e}")
        return None, None

def is_outdated(date_str):
    try:
        dt, _ = parse_date_get_timestamp(date_str)
        if not dt:
            return True
        return dt.date() != datetime.now().date()
    except:
        return True

async def get_vnexpress(url: str):
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

                article_resp = requests.get(article_url, headers=headers)
                if article_resp.status_code == 200:
                    article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                    sidebar_div = article_soup.find("div", class_="sidebar-1")

                    if sidebar_div:
                        header = ""
                        content_parts = []
                        date = ""
                        timestamp = None
                        image = None

                        span_tag = sidebar_div.find("span", class_="date")
                        if span_tag:
                            date = span_tag.get_text(strip=True)
                            dt, timestamp = parse_date_get_timestamp(date)
                            if is_outdated(date):
                                continue

                        h1_tag = sidebar_div.find("h1")
                        if h1_tag:
                            header = h1_tag.get_text(strip=True)

                        img_tags = sidebar_div.find_all("img")
                        for img in img_tags:
                            if img.has_attr('data-src'):
                                image = img['data-src'].replace("amp;", "")
                            elif img.has_attr('src'):
                                image = img['src'].replace("amp;", "")

                        p_tags = sidebar_div.find_all("p")
                        for p in p_tags:
                            text = p.get_text(strip=True)
                            if text:
                                content_parts.append(text)

                        article_data = {
                            "query": url,
                            "header": header,
                            "image": image,
                            "content": "\n".join(content_parts),
                            "date": date,
                            "timestamp": timestamp
                        }
                        results.append(article_data)
                    else:
                        print("⚠️ Không tìm thấy div.sidebar-1")
                else:
                    print(f"❌ Lỗi khi truy cập bài báo, status code: {article_resp.status_code}")

                time.sleep(1)
    else:
        print(f"❌ Lỗi khi tải trang chủ AI, status code: {response.status_code}")

    return results