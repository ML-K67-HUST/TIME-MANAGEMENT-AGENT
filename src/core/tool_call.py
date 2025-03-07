import openai
from src.config import settings
import json
from src.constants.tool_pool import FUNCTION_MAP
from src.constants.tool_pool import TOOL_TEST

client = openai.OpenAI(
    api_key=settings.together_api_key,
    base_url="https://api.together.xyz/v1",
)

messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]

completion = client.chat.completions.create(
    messages=messages,
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    tools=TOOL_TEST,
)
# print(completion)



if completion.choices[0].message.tool_calls:
    function_name = (completion.choices[0].message.tool_calls[0].function.name)
    function_arguments = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
    
    function_result = FUNCTION_MAP[function_name](**function_arguments)
    print(function_result)
