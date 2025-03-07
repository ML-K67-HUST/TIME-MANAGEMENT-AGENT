
from src.utils.function_calling import *
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
}]
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "domain_asking",
            "description": "Get information about effective time management",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question about time management"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "database_asking",
            "description": "Get information about user's info, tasks or schedule",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question about their information, their tasks or schedule"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "saving_constraint",
            "description": "Noting the time that user unavailable",
            "parameters": {
                "type": "object",
                "properties": {
                    "noting": {
                        "type": "string",
                        "description": "The user's message for time constraint"
                    }
                },
                "required": ["noting"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reading_constraint",
            "description": "Based on constraints, consider suggestion for scheduling",
            "parameters": {
                "type": "object",
                "properties": {
                    "asking": {
                        "type": "string",
                        "description": "Asking for task scheduling"
                    }
                },
                "required": ["asking"]
            }
        }
    },
    {
        "type":"function",
        "function": {
            "name": "database_addtask",
            "description": "Pass by parameters equivalent with information user gave you to ask their task",
            "parameters": {
                "type":"object",
                "properties": {
                    "taskName":{
                        "type":"string",
                        "description":"Name of the task"
                    },
                    "taskDescript": {
                        "type":"string",
                        "description":"Details description of the task."
                    },
                    "startTime":{
                        "type":"string",
                        "description":"Start time of the task, formatted in ISO 8601 : %Y-%m-%dT%H:%M:%S.%fZ"
                    },
                    "endTime":{
                        "type":"string",
                        "description":"End time of the task, formatted in ISO 8601 : %Y-%m-%dT%H:%M:%S.%fZ"
                    },
                    "taskColor":{
                        "type":"string",
                        "description":"color when display the task"
                    }    
                },
                "required":["taskName","startTime","endTime"]
            }
        }
    }
]

FUNCTION_MAP = {
    "get_weather":get_weather
}