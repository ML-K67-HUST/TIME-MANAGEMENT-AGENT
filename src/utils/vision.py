from google import genai
from google.genai import types
from config import settings
import requests
import os

def com_vision(url):
    client = genai.Client(api_key=settings.gemini_vision_api_key)
    query = "Describe the content of the image?"
    image = requests.get(url)
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[query,
                types.Part.from_bytes(data=image.content, mime_type="image/jpeg")])
    
    return response.text
