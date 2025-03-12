import openai
from config import settings
from constants.prompt_library import SYSTEM_PROMPT
from core.tool_call import execute_query
from utils.google_search import get_google_search, classify_prompt
from utils.format_message import *
from utils.conversation import update_history
from database.sqldb import *
async def generate_chat_completions(userid:int, token:str, prompt: str, history=[] , system_prompt=SYSTEM_PROMPT):
    client = openai.OpenAI(
        api_key=settings.together_api_key,
        base_url="https://api.together.xyz/v1",
    )
    print('INITIALIZED CLIENT')
    now = get_current_time_info()

    user_info=format_user_info(get_user_info(userid,token)) 

    task_history=format_task_message(get_user_tasks(userid, token))

    knowledge_message=""

    if classify_prompt(prompt):
        knowledges = await get_google_search(prompt)
        knowledge_message = format_google_search(knowledges)

    print('DID GG SEARCH')

    function_calling = execute_query(prompt)
    print('DID FC')

    messages = [
        {
            "role": "system", 
            "content": system_prompt.format(
                NOW_TIME=now, # done 
                MESSAGE=function_calling['result'], # done
                CONSTRAINT="",
                USER_INFO=user_info, 
                TASK_HISTORY=task_history,
                GG_MESSAGE=knowledge_message # done
            )
        },
    ]
    print('SYSTEM PROMPT:\n',messages)
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

    assistant = response.choices[0].message.content
    update_status = update_history(
        userid=userid,
        token=token,
        user=prompt,
        assistant=assistant
    )
    print('DID UPDATE HISTORY')
    print(f"update status: {update_status}")
    return assistant
