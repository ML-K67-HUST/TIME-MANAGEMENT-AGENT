import openai
import asyncio
import time
from config import settings
from constants.prompt_library import SYSTEM_PROMPT
from core.tool_call import execute_query_if_needed
# from utils.google_search import get_google_search, classify_prompt
from utils.format_message import *
from utils.conversation import update_history
from utils.user_cache import get_cached_user_info, get_cached_task_history, should_invalidate_task_cache, invalidate_task_cache
from utils.chat import infer
from utils.classifier import classify_prompt
from utils.vision import com_vision
from rag.query_from_vector_store import (
    query_for_about_us,
    query_for_domain_knowledge,
    query_for_task_management_tips
)
from database.sqldb import *
from database.discord import send_discord_notification
import contextvars
import functools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("chat_completion")

background_tasks = set()

async def generate_chat_completions(userid:int, token:str, prompt: str, history=[] ,image_url=None, system_prompt=SYSTEM_PROMPT):
    start_time_total = time.time()
    
    # client = openai.OpenAI(
    #     api_key=settings.together_api_key,
    #     base_url="https://api.together.xyz/v1",
    # )
    decider = classify_prompt(prompt)
    print("#### DECIDER: #### ",decider)
    # client = openai.OpenAI(
    #     api_key=settings.gemini_api_key,
    #     base_url=settings.gemini_base_url,
    # )
    

    start_time_tasks = time.time()
    user_info_task = asyncio.create_task(get_user_info_async(userid, token))
    task_history_task = asyncio.create_task(get_task_history_async(userid, token))
    function_calling_task = asyncio.create_task(execute_function_call_async(userid=userid,prompt=prompt,decider=decider["function_calling"]))
    
    start_time_now = time.time()
    now = get_current_time_info()
    logger.info(f"Time to get current time info: {time.time() - start_time_now:.4f}s")
    
    start_time_user_info = time.time()
    user_info = await user_info_task
    logger.info(f"Time to get user info: {time.time() - start_time_user_info:.4f}s")
    
    start_time_task_history = time.time()
    task_history = await task_history_task
    logger.info(f"Time to get task history: {time.time() - start_time_task_history:.4f}s")
    
    start_time_function_calling = time.time()
    function_calling = await function_calling_task
    logger.info(f"Time to execute function call: {time.time() - start_time_function_calling:.4f}s")
    
    # logger.info(f"Total time for all async tasks: {time.time() - start_time_tasks:.4f}s")

    start_time_about_us = time.time()
    about_us = query_for_about_us(prompt, decider=decider["about_us"])
    logger.info(f"Time to query about us: {time.time() - start_time_about_us:.4f}s")

    start_time_about_us = time.time()
    domain_knowledge = query_for_domain_knowledge(prompt, decider=decider["domain_knowledge"])
    logger.info(f"Time to query knowledge message: {time.time() - start_time_about_us:.4f}s")

    start_time_about_us = time.time()
    time_management_tips = query_for_task_management_tips(prompt, decider=decider["task_management"])
    logger.info(f"Time to query time management tips: {time.time() - start_time_about_us:.4f}s")
  
    start_time_format_messages = time.time()
    
    img_info = "No image provided"
    if image_url and image_url.startswith("http"):
        start_time_about_us = time.time()
        img_info = com_vision(image_url)
        logger.info(f"Time to get img info: {time.time() - start_time_about_us:.4f}s")

    
    formatted_system_prompt = system_prompt.format(
        NOW_TIME=now,
        MESSAGE=function_calling['result'],
        ABOUT_US=about_us,
        USER_INFO=user_info, 
        TASK_HISTORY=task_history,
        TIME_MANAGEMENT=time_management_tips,
        DOMAIN_KNOWLEDGE=domain_knowledge,
        PICTURE_DESCRIPTION=img_info
    )
    send_discord_notification(
        prompt, formatted_system_prompt
    )
    
    logger.info(f"System prompt size: {len(formatted_system_prompt)} characters")
    # print(f"System prompt content: {formatted_system_prompt[:500]}... (truncated)")
    # print("FUNCTION CALLING: ",function_calling['result'])
    # logger.info(f"Component sizes - NOW_TIME: {len(str(now))}, MESSAGE: {len(str(function_calling['result']))}, "
    #             f"ABOUT_US: {len(str(about_us))}, USER_INFO: {len(str(user_info))}, "
    #             f"TASK_HISTORY: {len(str(task_history))}, TIME_MANAGEMENT: {len(str(time_management_tips))}, "
    #             f"DOMAIN_KNOWLEDGE: {len(str(domain_knowledge))}")
    
    messages = [
        {
            "role": "system", 
            "content": formatted_system_prompt
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
    logger.info(f"Time to format messages: {time.time() - start_time_format_messages:.4f}s")
    
    # response = client.chat.completions.create(
    #     model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    #     messages=messages,
    #     temperature=0.7,
    #     max_tokens=800,
    # )
    start_time_llm = time.time()
    # response = client.chat.completions.create(
    #     model="gemini-2.0-flash",
    #     messages=messages,
    #     temperature=0.7,
    #     max_tokens=5000,
    # )
    # response = generate_chat_completions(
    #     api_key=settings.gemini_api_key,
    #     base_url=settings.gemini_base_url,
    #     model_name="gemini-2.0-flash",
    #     messages=messages
    # )
    response = await infer(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
        model_name="gemini-2.0-flash",
        messages=messages
    )
    logger.info(f"Time for LLM response: {time.time() - start_time_llm:.4f}s")
    # response = generate_chat_completion_openai(
    #     messages=messages
    # )
    assistant = response.choices[0].message.content
    # assistant = response["choices"][0]["message"]["content"]
    
    start_time_background = time.time()
    loop = asyncio.get_running_loop()
    background_task = loop.create_task(
        update_history_and_cache(userid, token, prompt, assistant)
    )
    
    background_tasks.add(background_task)
    background_task.add_done_callback(
        lambda t: background_tasks.remove(t)
    )
    logger.info(f"Time to set up background task: {time.time() - start_time_background:.4f}s")
    
    logger.info(f"Total time for chat completion: {time.time() - start_time_total:.4f}s")
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

async def execute_function_call_async(userid, prompt, decider):
    print("1")
    return execute_query_if_needed(userid=userid, query=prompt,decider=decider)
