import os
import json
import requests
from datetime import datetime
### TEST
def get_user_name():
    return "user's name: dinh van dang"
def get_weather(latitude, longitude):
    return "the current temperature: 39 celcius"

### FUNCTIONS FOR MODIFYING USER CALENDAR

def add_single_task(data):

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    # json_data = {
    #     'userid': '7',
    #     'task_name': 'hit gym',
    #     'task_description': 'with John',
    #     'start_time': 123,
    #     'end_time': 321,
    #     'color': 'red',
    #     'status': 'in progress',
    #     'priority': 2,
    # }
    
    response = requests.post('http://grand-backend.fly.dev/sqldb/tasks/', headers=headers, json=data)
    if response.status_code == 200:
        return "Add task success !!"
    else:
        return "Error when add task"

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