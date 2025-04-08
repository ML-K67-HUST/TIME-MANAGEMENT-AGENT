import sys
import os
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from database.vector_store import MilvusClient
from database.memory_store import MemoryStore
import openai
from config import settings

def get_embedding(text):
    """
    Get an embedding for a text using OpenAI's embedding API.
    This is just an example, you can use any embedding function.
    """
    client = openai.OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
    )
    
    response = client.embeddings.create(
        model="textembedding-gecko@latest",
        input=text
    )
    
    return response.data[0].embedding

def milvus_basic_example():
    """Example of basic Milvus operations"""
    print("=== Basic Milvus Operations ===")
    
    # Initialize Milvus client
    milvus = MilvusClient()
    
    # Create a test collection
    collection_name = "test_collection"
    milvus.create_collection(collection_name, dim=768)  # 768 is the dimension of the embeddings
    
    # List all collections
    print(f"Collections: {milvus.list_collections()}")
    
    # Generate some test data
    texts = [
        "The weather is nice today.",
        "I enjoy programming in Python.",
        "Vector databases are useful for semantic search.",
        "Machine learning models can be challenging to deploy."
    ]
    
    # Generate embeddings
    vectors = [get_embedding(text) for text in texts]
    
    # Add metadata
    metadatas = [
        {"source": "weather", "category": "small_talk"},
        {"source": "programming", "category": "technical"},
        {"source": "databases", "category": "technical"},
        {"source": "ml", "category": "technical"}
    ]
    
    # Insert vectors
    ids = milvus.insert_vectors(
        collection_name=collection_name,
        vectors=vectors,
        texts=texts,
        metadatas=metadatas
    )
    
    print(f"Inserted {len(ids)} vectors with IDs: {ids}")
    
    # Search by vector
    query_text = "Is Python a good programming language?"
    query_vector = get_embedding(query_text)
    
    results = milvus.search_by_vector(
        collection_name=collection_name,
        query_vector=query_vector,
        top_k=2
    )
    
    print(f"\nSearch results for '{query_text}':")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['text']} (Score: {result['score']:.4f})")
    
    # Clean up (optional)
    # milvus.drop_collection(collection_name)
    print("Basic example completed.")

def memory_store_example():
    """Example of using the MemoryStore class"""
    print("\n=== Memory Store Operations ===")
    
    # Initialize MemoryStore
    memory_store = MemoryStore()
    memory_store.set_embedding_function(get_embedding)
    
    # Add a single memory
    memory_id = memory_store.add_memory(
        text="The capital of France is Paris.",
        metadata={"topic": "geography", "confidence": "high"},
        user_id="user123"
    )
    
    print(f"Added memory with ID: {memory_id}")
    
    # Add multiple memories
    memories = [
        "Python is a programming language.",
        "The Earth orbits around the Sun.",
        "Machine learning is a subset of artificial intelligence."
    ]
    
    metadata = [
        {"topic": "programming", "confidence": "high"},
        {"topic": "astronomy", "confidence": "high"},
        {"topic": "ai", "confidence": "medium"}
    ]
    
    memory_ids = memory_store.add_memories(
        texts=memories,
        metadatas=metadata,
        user_id="user123"
    )
    
    print(f"Added {len(memory_ids)} memories with IDs: {memory_ids}")
    
    # Search for relevant memories
    query = "Tell me about computer programming"
    
    results = memory_store.search_memories(
        query=query,
        user_id="user123",
        top_k=2
    )
    
    print(f"\nSearch results for '{query}':")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['text']} (Score: {result['score']:.4f})")
    
    # Get formatted memories for use in prompts
    formatted_memories = memory_store.get_relevant_memories(
        query=query,
        user_id="user123",
        top_k=2
    )
    
    print(f"\nFormatted memories for prompt:\n{formatted_memories}")
    
    print("Memory store example completed.")

if __name__ == "__main__":
    try:
        milvus_basic_example()
        memory_store_example()
    except Exception as e:
        print(f"Error: {str(e)}")
        
    print("\nNote: Make sure Milvus server is running. You can start it with Docker:")
    print("docker run -d --name milvus_standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest standalone") 