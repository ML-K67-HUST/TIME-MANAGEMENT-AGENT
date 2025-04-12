import os
import json
import requests
from datetime import datetime
from utils.format_message import iso_to_timestamp, format_task_message_for_bot
from config import settings
### TEST
def get_user_name():
    return "user's name: dinh van dang"
def get_weather(latitude, longitude):
    return "the current temperature: 39 celcius"

### FUNCTIONS FOR MODIFYING USER CALENDAR

## ADD SINGLE TASK TO DATABASE
def add_single_task_to_database(
        userid, 
        task_name:str,
        start_time:int,
        end_time:int,
        task_description:str = "",
        color:str = "#0000ff",
        status:str = "pending",
        priority:int = 0
    ):
    """
    Thêm task vào lịch, schema cho trước, dùng api query db

	
    Sample Response 
    {
    "message": "✅ Task created!",
    "task": {
        "taskid": "ccf1082c-5bbd-4134-90f9-7ef025f7b10f",
        "userid": "7",
        "task_name": "tét",
        "task_description": "tét",
        "start_time": 0,
        "end_time": 10,
        "color": "red",
        "status": "pending",
        "priority": 0
    }
    }
    """
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    start_time = iso_to_timestamp(start_time)
    end_time = iso_to_timestamp(end_time)
    json_data = {   
        'userid': str(userid),
        'task_name': task_name,
        'task_description': task_description,
        'start_time': start_time,
        'end_time': end_time,
        'color': color,
        'status': status,
        'priority': priority,
    }
    print("Trying to add task to database, data:\n",json_data)


    response = requests.post(f'{settings.backend_url}/sqldb/tasks/', headers=headers, json=json_data)
    if response.status_code == 200:
        tasks = response.json()
        tasks["task"]["start_time"] = start_time
        tasks["task"]["end_time"] = end_time
        return format_task_message_for_bot(tasks)
    else:
        print("error, status code: ", response.status_code)
        print("detailed of error: ", response.text)
        return "Failed to add task to database"

def get_feasible_update_tasks():
    # Gen query để query trên chromadb -> thực hiện query trên db chroma tasks -> lấy được hết tasks liên quan về

    # lưu vào cache một pair (tasks, query_to_modify)

    # Format tasks rồi return, hỏi xác nhận thay đổi

    pass    

def update_tasks(
        data,
        start_time,
    ):
    # lấy ra cache các cặp pair (tasks, query_to_modify) rồi gọi execution function để thay đổi

    # xoá pair đó khỏi cache

    # return update
    pass

def get_feasible_delete_tasks(
        data, 
        start_time,
    ):
    pass

def delete_tasks(data):
    pass

### SAVE CONSTRAINT
def saving_constraint(content):
    pass

# LOAD CONSTRAINT
def reading_constraint(query):
    pass