from database.caching import redis_cache
from database.sqldb import get_user_info, get_user_tasks
from utils.format_message import format_user_info, format_task_message

def get_cached_user_info(userid, token):
    """
    Get user info from cache or database if not cached.
    
    Args:
        userid (int): User ID
        token (str): Authentication token
        
    Returns:
        dict: Formatted user info
    """
    cache_key = f"user_info:{userid}:{token}"
    cached_data = redis_cache.get(cache_key)
    
    if cached_data:
        print("Using cached user info")
        return cached_data
    
    print("Fetching user info from database")
    db_user_info = get_user_info(userid, token)
    formatted_data = format_user_info(db_user_info)
    redis_cache.set(cache_key, formatted_data, ttl=3600)  # Cache for 1 hour
    return formatted_data

def get_cached_task_history(userid, token):
    """
    Get task history from cache or database if not cached.
    
    Args:
        userid (int): User ID
        token (str): Authentication token
        
    Returns:
        str: Formatted task message
    """
    cache_key = f"user_tasks:{userid}:{token}"
    cached_data = redis_cache.get(cache_key)
    
    if cached_data:
        print("Using cached task history")
        return cached_data
    
    print("Fetching task history from database")
    db_tasks = get_user_tasks(userid, token)
    formatted_data = format_task_message(db_tasks)
    redis_cache.set(cache_key, formatted_data, ttl=1800)  # Cache for 30 minutes
    return formatted_data

def invalidate_task_cache(userid, token):
    """
    Invalidate task cache for a specific user.
    
    Args:
        userid (int): User ID
        token (str): Authentication token
        
    Returns:
        bool: True if successful, False otherwise
    """
    cache_key = f"user_tasks:{userid}:{token}"
    return redis_cache.delete(cache_key)

def should_invalidate_task_cache(prompt):
    """
    Check if the prompt suggests task-related changes that should invalidate the cache.
    
    Args:
        prompt (str): User prompt
        
    Returns:
        bool: True if cache should be invalidated, False otherwise
    """
    task_related_keywords = [
        "task", "todo", "to-do", "schedule", "plan", "appointment", 
        "meeting", "reminder", "deadline", "complete", "finish",
        "add", "create", "update", "delete", "remove", "change"
    ]
    
    prompt_lower = prompt.lower()
    for keyword in task_related_keywords:
        if keyword in prompt_lower:
            return True
    
    return False 