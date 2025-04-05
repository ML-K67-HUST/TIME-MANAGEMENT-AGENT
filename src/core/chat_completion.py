import openai
import asyncio
from config import settings
from constants.prompt_library import SYSTEM_PROMPT
from core.tool_call import execute_query_if_needed
from utils.google_search import get_google_search, classify_prompt
from utils.format_message import *
from utils.conversation import update_history
from utils.user_cache import get_cached_user_info, get_cached_task_history, should_invalidate_task_cache, invalidate_task_cache
from database.sqldb import *

async def generate_chat_completions(userid:int, token:str, prompt: str, history=[] , system_prompt=SYSTEM_PROMPT):
    client = openai.OpenAI(
        api_key=settings.together_api_key,
        base_url="https://api.together.xyz/v1",
    )
    
    user_info_task = asyncio.create_task(get_user_info_async(userid, token))
    task_history_task = asyncio.create_task(get_task_history_async(userid, token))
    function_calling_task = asyncio.create_task(execute_function_call_async(prompt))
    
    now = get_current_time_info()
    
    user_info = await user_info_task
    task_history = await task_history_task
    function_calling = await function_calling_task
    
    knowledge_message = ""

    messages = [
        {
            "role": "system", 
            "content": system_prompt.format(
                NOW_TIME=now,
                MESSAGE=function_calling['result'],
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
    
    # Optimize completion parameters
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages,
        temperature=0.7,  # Slightly lower temperature for more focused responses
        max_tokens=800,   # Limit token generation to what's needed
        # stream=True,
    )

    assistant = response.choices[0].message.content
    update_status = update_history(
        userid=userid,
        token=token,
        user=prompt,
        assistant=assistant
    )
    
    # If tasks were updated or user made changes, invalidate cache
    if should_invalidate_task_cache(prompt):
        invalidate_task_cache(userid, token)
    
    return assistant

# Async helper functions to allow concurrent execution
async def get_user_info_async(userid, token):
    """Get user info asynchronously"""
    return get_cached_user_info(userid, token)

async def get_task_history_async(userid, token):
    """Get task history asynchronously"""
    return get_cached_task_history(userid, token)

async def execute_function_call_async(prompt):
    """Execute function call asynchronously"""
    # Run in a thread pool to prevent blocking
    return await asyncio.to_thread(execute_query_if_needed, prompt)
