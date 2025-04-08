import openai
import asyncio
from config import settings
from constants.prompt_library import SYSTEM_PROMPT
from core.tool_call import execute_query_if_needed
from utils.google_search import get_google_search, classify_prompt
from utils.format_message import *
from utils.conversation import update_history
from utils.user_cache import get_cached_user_info, get_cached_task_history, should_invalidate_task_cache, invalidate_task_cache
from utils.chat import generate_chat_completion_openai
from rag.query_from_vector_store import query_for_about_us
from database.sqldb import *
import contextvars
import functools

background_tasks = set()

async def generate_chat_completions(userid:int, token:str, prompt: str, history=[] , system_prompt=SYSTEM_PROMPT):
    # client = openai.OpenAI(
    #     api_key=settings.together_api_key,
    #     base_url="https://api.together.xyz/v1",
    # )
    client = openai.OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
    )
    
    user_info_task = asyncio.create_task(get_user_info_async(userid, token))
    task_history_task = asyncio.create_task(get_task_history_async(userid, token))
    function_calling_task = asyncio.create_task(execute_function_call_async(prompt))
    
    now = get_current_time_info()
    
    user_info = await user_info_task
    task_history = await task_history_task
    function_calling = await function_calling_task
    
    knowledge_message = ""
    about_us = query_for_about_us(prompt)

    messages = [
        {
            "role": "system", 
            "content": system_prompt.format(
                NOW_TIME=now,
                MESSAGE=function_calling['result'],
                ABOUT_US=about_us,
                CONSTRAINT="",
                USER_INFO=user_info, 
                TASK_HISTORY=task_history,
                GG_MESSAGE=knowledge_message
            )
        },
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
    
    # response = client.chat.completions.create(
    #     model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    #     messages=messages,
    #     temperature=0.7,
    #     max_tokens=800,
    # )
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=messages,
        temperature=0.7,
        max_tokens=800,
    )
    # response = generate_chat_completion_openai(
    #     messages=messages
    # )
    assistant = response.choices[0].message.content
    # assistant = response["choices"][0]["message"]["content"]
    

    loop = asyncio.get_running_loop()
    background_task = loop.create_task(
        update_history_and_cache(userid, token, prompt, assistant)
    )
    
    background_tasks.add(background_task)
    background_task.add_done_callback(
        lambda t: background_tasks.remove(t)
    )
    
    return assistant

async def update_history_and_cache(userid, token, prompt, assistant):
    """
    Update conversation history and handle cache invalidation in the background.
    This runs asynchronously after the response has been sent to the user.
    """
    try:
        update_status = update_history(
            userid=userid,
            token=token,
            user=prompt,
            assistant=assistant
        )
        
        if should_invalidate_task_cache(prompt):
            invalidate_task_cache(userid, token)
            
        return True
    except Exception as e:
        print(f"Error in background task: {str(e)}")
        return False

async def get_user_info_async(userid, token):
    return get_cached_user_info(userid, token)

async def get_task_history_async(userid, token):
    return get_cached_task_history(userid, token)

async def execute_function_call_async(prompt):
    return await asyncio.to_thread(execute_query_if_needed, prompt)
