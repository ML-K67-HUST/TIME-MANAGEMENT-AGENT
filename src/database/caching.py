import redis
import json
import os
from config import settings
import time

class RedisCache:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
            redis_url = os.getenv("REDIS_URL", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_password = os.getenv("REDIS_PASSWORD", "")
            
            cls._instance.client = redis.Redis(
                host=redis_url,
                port=redis_port,
                password=redis_password,
                ssl=True,
                decode_responses=True
            )
            
            try:
                cls._instance.client.ping()
                print("Successfully connected to Redis")
            except Exception as e:
                print(f"Failed to connect to Redis: {str(e)}")
                cls._instance.client = None
        
        return cls._instance
    
    def get(self, key):
        if not self.client:
            return None
            
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {str(e)}")
            return None
    
    def set(self, key, value, ttl=3600):
        if not self.client:
            return False
            
        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Redis set error: {str(e)}")
            return False
    
    def delete(self, key):
        if not self.client:
            return False
            
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {str(e)}")
            return False
    
    def clear_user_cache(self, userid, token):
        if not self.client:
            return False
            
        try:
            self.delete(f"user_info:{userid}:{token}")
            self.delete(f"user_tasks:{userid}:{token}")
            return True
        except Exception as e:
            print(f"Redis clear cache error: {str(e)}")
            return False

redis_cache = RedisCache() 