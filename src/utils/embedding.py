import openai
from config import settings

def get_embedding(text):
    """
    Generate embeddings for a text string using OpenAI's API.
    
    Args:
        text (str): Text to generate embedding for
        
    Returns:
        list: Vector embedding representation of the text
    """
    try:
        client = openai.OpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
        )
        
        response = client.embeddings.create(
            model="textembedding-gecko@latest",
            input=text
        )
        
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        # Return a dummy embedding for graceful failure
        # This is just a fallback; in production, handle this more robustly
        return [0.0] * 768  # Google's textembedding-gecko has 768 dimensions 