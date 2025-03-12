import openai
import json
from config import settings
from constants.tool_pool import FUNCTION_MAP, TOOL_TEST

client = openai.OpenAI(
    api_key=settings.together_api_key,
    base_url="https://api.together.xyz/v1",
)

def execute_query(query: str):
    messages = [{"role": "user", "content": query}]

    completion = client.chat.completions.create(
        messages=messages,
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        tools=TOOL_TEST,
    )

    tool_calls = completion.choices[0].message.tool_calls

    if tool_calls:
        function_name = tool_calls[0].function.name
        function_arguments = json.loads(tool_calls[0].function.arguments)

        if function_name in FUNCTION_MAP:
            return {
                'function': function_name,
                'args': function_arguments,
                'result': FUNCTION_MAP[function_name](**function_arguments)
            } 

    return {
        'function': None,
        'args': None,
        'result': ""
    } 
