import os
from dotenv import load_dotenv

load_dotenv(override=True)

                
class Settings:
    def __init__(self):
        self.together_api_key = os.getenv("TOGETHER_AI_API_KEY")
        self.together_base_url = "https://api.together.xyz/v1"

        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        self.glm_api_key = os.getenv("GLM_API_KEY")
        self.glm_base_url = "https://open.bigmodel.cn/api/paas/v4" 
        self.gpt_nha_lam_api_key = "deo-can"
        self.gpt_nha_lam_base_url = "http://gpt-nha-lam:8080/v1"
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.mongodb_timenest_db_name = os.getenv("MONGDB_TIMENEST_DN_NAME")
        self.chroma_endpoint = os.getenv("chroma_client_url")
        self.chroma_model = os.getenv("chroma_model")
        self.embedding_client_url = os.getenv("embedding_client_url")
        self.gemini_vision_api_key = os.getenv("GEMINI_VISION_API_KEY")
        self.backend_url = os.getenv("BACKEND_URL")
        self.vector_store_url = os.getenv("VECTOR_STORE_URL")
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.discord_fc_webhook_url = os.getenv("DISCORD_FC_WEBHOOK_URL")
settings = Settings()