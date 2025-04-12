import json
from datetime import datetime
from zoneinfo import ZoneInfo 

def get_current_time_info():
    now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
    today_str = now.strftime("%Y-%m-%d, %H:%M GMT+7")
    hour = now.hour

    time_of_day = (
        "morning" if 5 <= hour < 12
        else "afternoon" if 12 <= hour < 18
        else "night"
    )
    print(F"DATETIME NOW: {today_str, time_of_day}")
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

def iso_to_timestamp(iso_string: str) -> int:
    dt = datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    return int(dt.timestamp())-25200

def format_task_message_for_bot(data: dict) -> str:
    if not data or "task" not in data:
        return "No task data found."

    task = data["task"]
    lines = [
        data.get("message", "Task info:"),
        f"Detailed Information:",
        f"User ID: {task.get('userid')}",
        f"Name: {task.get('task_name')}",
        f"Description: {task.get('task_description')}",
        f"Start Time: {task.get('start_time')}",
        f"End Time: {task.get('end_time')}",
        f"Color: {task.get('color')}",
        f"Status: {task.get('status')}",
        f"Priority: {task.get('priority')}",
    ]
    return "\n".join(lines)