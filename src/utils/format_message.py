import json
from datetime import datetime


def get_current_time_info():
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d, %H:%M UTC")
    hour = now.hour
    
    time_of_day = "morning" if 5 <= hour < 12 \
        else "afternoon" if 12 <= hour < 18 \
        else "night"
    
    return today_str, time_of_day


def format_user_info(user_data: dict) -> str:
    user = user_data.get("user", {})
    full_name = user.get("full_name", "Unknown")
    username = user.get("username", "Unknown")
    email = user.get("email", "Unknown")
    
    return f"User: {full_name} (Username: {username}, Email: {email})"

def format_google_search(knowledges):
    message = ""
    for knowledge in knowledges:
        message += f"website of url:`{knowledge['url']}` have knowledge: `{knowledge['answer']}`\n\n"
    return message

def format_task_message(task_data: dict) -> str:
    user_id = task_data.get("userid", "Unknown")
    tasks = task_data.get("tasks", [])
    
    task_dict = {}
    for task in tasks:
        task_date = datetime.utcfromtimestamp(task["start_time"]).strftime("%Y-%m-%d")
        time_of_day = "morning" if 5 <= datetime.utcfromtimestamp(task["start_time"]).hour < 12 \
            else "afternoon" if 12 <= datetime.utcfromtimestamp(task["start_time"]).hour < 18 \
            else "night"
        
        if task_date not in task_dict:
            task_dict[task_date] = {"morning": [], "afternoon": [], "night": []}
        
        start_time = datetime.utcfromtimestamp(task["start_time"]).strftime("%H:%M")
        end_time = datetime.utcfromtimestamp(task["end_time"]).strftime("%H:%M")
        
        task_dict[task_date][time_of_day].append(
            f"- {task['task_name']} ({task['status']}): {task['task_description']} [Color: {task['color']}, Priority: {task['priority']}, Time: {start_time} -> {end_time}]"
        )
    
    formatted_tasks = []
    for date, periods in sorted(task_dict.items()):
        formatted_tasks.append(f"{date}:")
        for period, task_list in periods.items():
            if task_list:
                formatted_tasks.append(f"  {period}:")
                formatted_tasks.extend([f"    {task}" for task in task_list])
    
    task_list_str = "\n".join(formatted_tasks) if formatted_tasks else "No tasks found."
    
    system_prompt = (
        f"User has defined the following tasks in the past:\n"
        f"{task_list_str}\n\n"
    )
    
    return system_prompt
