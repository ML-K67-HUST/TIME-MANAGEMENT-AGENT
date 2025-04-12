import openai
import json
import time
from config import settings
from constants.tool_pool import FUNCTION_MAP, TOOL_TEST,TOOLS
from constants.prompt_library import FUNCTION_CALLING_PROMPT
from database.discord import send_discord_fc_notification
from utils.format_message import get_current_time_info
from database.caching import redis_cache

client = openai.OpenAI(
    api_key=settings.gemini_api_key,
    # base_url="https://api.together.xyz/v1",
    base_url=settings.gemini_base_url
)

FUNCTION_CACHE_TTL = 600

def execute_query(userid,query: str):
    print(3)
    """
    Execute a function call based on the user query with caching.
    
    Args:
        query (str): User query
        
    Returns:
        dict: Function execution result
    """
    cache_key = f"function_call:{hash(query)}"
    cached_result = redis_cache.get(cache_key)
    if cached_result:
        print("Using cached function call result")
        return cached_result
    
    start_time = time.time()
    messages = [
        {"role": "system", "content": FUNCTION_CALLING_PROMPT.format(
            NOW_TIME=get_current_time_info()
        )},
        {"role": "user", "content": query}
    ]

    completion = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
        # temperature=0.1,  # Lower temperature for more deterministic outputs
        # max_tokens=300,   # Limit token generation to what's needed
        # top_p=0.9,        # Focus on more likely tokens
    )

    tool_calls = completion.choices[0].message.tool_calls


    print("tool calls: ",  tool_calls)
    result = {
        'function': None,
        'args': None,
        'result': "You did nothing"
    }

    if tool_calls:
        function_name = tool_calls[0].function.name
        function_arguments = json.loads(tool_calls[0].function.arguments)
        # print("FUNCTION ARGS: ",function_arguments)
        function_arguments["userid"] = userid
        if function_name in FUNCTION_MAP:
            return_value = FUNCTION_MAP[function_name](**function_arguments)
            result = {
                'function': function_name,
                'args': function_arguments,
                'result': return_value
            }
            send_discord_fc_notification(
                prompt=query,
                function_name=function_name,
                function_args=function_arguments,
                result=return_value
            )

    redis_cache.set(cache_key, result, ttl=FUNCTION_CACHE_TTL)
    
    end_time = time.time()
    print(f"Function calling took {end_time - start_time:.2f} seconds")
    
    return result
    
def execute_query_if_needed(userid, query: str, decider, force_execution=False):
    """
    Execute a function call only if the query likely requires a tool.
    
    Args:
        query (str): User query
        force_execution (bool): Force execution regardless of heuristics
        
    Returns:
        dict: Function execution result or empty result
    """
    print(2)
    if not decider:
        return {
            'result':"You did nothing"
        }

    
    return execute_query(userid,query)

def likely_needs_function_call(query: str):
    """
    Use heuristics to determine if a query likely needs a function call.
    
    Args:
        query (str): User query
        
    Returns:
        bool: True if the query likely needs a function call
    """
    function_keywords = [
        "search", "lookup", "find", "calculate", "convert",
        "what is", "when is", "where is", "how many", "how much",
        "weather", "time", "date", "today", "tomorrow",
        "schedule", "task", "reminder", "calendar", "meeting",
        "factual", "information", "data", "stats", "statistics"
    ]
    
    query_lower = query.lower()
    
    has_question_mark = "?" in query
    has_function_keyword = any(keyword in query_lower for keyword in function_keywords)
    
    return has_question_mark or has_function_keyword 
