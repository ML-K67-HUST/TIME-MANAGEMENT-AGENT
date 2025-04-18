import os
from dotenv import load_dotenv

load_dotenv(override=True)

                
class Settings:
    def __init__(self):
        self.together_api_key = os.getenv("TOGETHER_AI_API_KEY")
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.mongodb_timenest_db_name = os.getenv("MONGDB_TIMENEST_DN_NAME")
        self.chroma_endpoint = os.getenv("chroma_client_url")
        self.chroma_model = os.getenv("chroma_model")
        self.embedding_client_url = os.getenv("embedding_client_url")
        self.gemini_vision_api_key = os.getenv("GEMINI_VISION_API_KEY")
        self.backend_url = os.getenv("BACKEND_URL")
settings = Settings()