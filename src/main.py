import requests
from config import settings
import time

def run_app_server():
    from uvicorn import run

    max_retries = 5
    retry_delay = 3  
    
    vector_store_available = False
    for attempt in range(max_retries):
        try:
            vector_store_response = requests.get(f'{settings.vector_store_url}', timeout=5)
            if vector_store_response.status_code == 200:
                print(f"Vector store available 🚀 (attempt {attempt+1}/{max_retries})")
                vector_store_available = True
                break
            else:
                print(f"Vector store returned status {vector_store_response.status_code} (attempt {attempt+1}/{max_retries})")
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to vector store (attempt {attempt+1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    if not vector_store_available:
        print("Vector store unavailable after all retries ❌")
    
    backend_available = False
    for attempt in range(max_retries):
        try:
            backend_response = requests.get(f'{settings.backend_url}/health_check/', timeout=5)
            if backend_response.status_code == 200:
                print(f"Backend available 🚀 (attempt {attempt+1}/{max_retries})")
                backend_available = True
                break
            else:
                print(f"Backend returned status {backend_response.status_code} (attempt {attempt+1}/{max_retries})")
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to backend (attempt {attempt+1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    if not backend_available:
        print("Backend unavailable after all retries ❌")
    
    run(
        "app:app",
        host="0.0.0.0",
        port=5001,
        # workers=int(settings.WORKERS),
        workers=1,
        # reload=True,
        # reload=os.getenv("RELOADS", "0") == "1"
    )


if __name__ == "__main__":
    run_app_server()