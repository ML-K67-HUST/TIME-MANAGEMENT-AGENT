from google import genai
from google.genai import types

import requests
import os
image_path = "https://goo.gle/instrument-img"
image = requests.get(image_path)

client = genai.Client(api_key='AIzaSyDxy33gXMEJoJvKXCexD2R4ZH5Z5aRgyWI')
query = "What is the instrument in the image?"
def com_vision(image_path):

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[query,
                types.Part.from_bytes(data=image.content, mime_type="image/jpeg")])
    
    return response.text
