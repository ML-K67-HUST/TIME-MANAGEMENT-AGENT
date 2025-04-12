
from utils.function_calling import *
TOOL_TEST = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",
    "function": {
        "name": "get_user_name",
        "description": "Get the full name of your person you chatting with ",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    }
}
]
TOOLS = [
    {
        "type":"function",
        "function": {
            "name": "add_single_task_to_database",
            "description": "Pass by parameters equivalent with information user gave you to ask their task",
            "parameters": {
                "type":"object",
                "properties": {
                    "task_name":{
                        "type":"string",
                        "description":"Name of the task"
                    },
                    "task_description": {
                        "type":"string",
                        "description":"Details description of the task."
                    },
                    "start_time":{
                        "type":"string",
                        "description":"Start time of the task, formatted in ISO 8601 : %Y-%m-%dT%H:%M:%S.%fZ"
                    },
                    "end_time":{
                        "type":"string",
                        "description":"End time of the task, formatted in ISO 8601 : %Y-%m-%dT%H:%M:%S.%fZ"
                    },
                    "color":{
                        "type":"string",
                        "description":"color when display the task"
                    },
                    "status":{
                        "type":"string",
                        "description":"status of the task"
                    },
                    "priority":{
                        "type":"integer",
                        "description":"priority of the task"
                    }
                },
                "required":["task_name","start_time","end_time"]
            }
        }
    }
]

FUNCTION_MAP = {
    "get_weather":get_weather,
    "get_user_name":get_user_name,
    "add_single_task_to_database":add_single_task_to_database
}