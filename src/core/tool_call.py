import openai
import json
import time
from config import settings
from constants.tool_pool import FUNCTION_MAP, TOOL_TEST
from database.caching import redis_cache

client = openai.OpenAI(
    api_key=settings.together_api_key,
    base_url="https://api.together.xyz/v1",
)

FUNCTION_CACHE_TTL = 600

def execute_query(query: str):
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
    messages = [{"role": "user", "content": query}]

    completion = client.chat.completions.create(
        messages=messages,
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        tools=TOOL_TEST,
        temperature=0.1,  # Lower temperature for more deterministic outputs
        max_tokens=300,   # Limit token generation to what's needed
        top_p=0.9,        # Focus on more likely tokens
    )

    tool_calls = completion.choices[0].message.tool_calls
    
    result = {
        'function': None,
        'args': None,
        'result': ""
    }

    if tool_calls:
        function_name = tool_calls[0].function.name
        function_arguments = json.loads(tool_calls[0].function.arguments)

        if function_name in FUNCTION_MAP:
            result = {
                'function': function_name,
                'args': function_arguments,
                'result': FUNCTION_MAP[function_name](**function_arguments)
            }
    
    redis_cache.set(cache_key, result, ttl=FUNCTION_CACHE_TTL)
    
    end_time = time.time()
    print(f"Function calling took {end_time - start_time:.2f} seconds")
    
    return result
    
def execute_query_if_needed(query: str, decider: bool, force_execution=False):
    """
    Execute a function call only if the query likely requires a tool.
    
    Args:
        query (str): User query
        force_execution (bool): Force execution regardless of heuristics
        
    Returns:
        dict: Function execution result or empty result
    """
    if not decider:
        return {
            'result':"No need to execute database modification"
        }
    if not force_execution and not likely_needs_function_call(query):
        return {
            'function': None,
            'args': None,
            'result': ""
        }
    
    return execute_query(query)

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
