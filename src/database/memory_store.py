from database.vector_store import MilvusClient
from utils.user_cache import redis_cache
import hashlib
import json
import os
from config import settings

class MemoryStore:
    """
    A higher-level abstraction for managing memory/knowledge in vector storage.
    Uses Milvus for vector storage and provides methods for adding and retrieving memories.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MemoryStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, embedding_function=None):
        if self._initialized:
            return
        
        # Initialize Milvus client
        self.milvus = MilvusClient()
        
        # Set embedding function
        self.embedding_function = embedding_function
        
        # Default collection name
        self.default_collection = os.getenv("MILVUS_DEFAULT_COLLECTION", "user_memory")
        
        # Ensure the default collection exists
        self._ensure_default_collection()
        
        self._initialized = True
    
    def _ensure_default_collection(self):
        """Make sure the default collection exists"""
        try:
            self.milvus.create_collection(self.default_collection)
        except Exception as e:
            print(f"Error creating default collection: {str(e)}")
    
    def set_embedding_function(self, embedding_function):
        """
        Set the embedding function to use for converting text to vectors.
        
        Args:
            embedding_function (callable): Function that converts text to a vector
        """
        self.embedding_function = embedding_function
    
    def add_memory(self, text, metadata=None, user_id=None, collection_name=None):
        """
        Add a new memory/document to the store.
        
        Args:
            text (str): The text content to store
            metadata (dict): Additional metadata about the memory
            user_id (str): Optional user ID to associate with the memory
            collection_name (str): Optional collection name (defaults to user_memory)
            
        Returns:
            int: ID of the inserted memory
        """
        if self.embedding_function is None:
            raise ValueError("Embedding function not set")
        
        # Set default collection
        collection_name = collection_name or self.default_collection
        
        # Set default metadata
        if metadata is None:
            metadata = {}
        
        # Add user_id to metadata if provided
        if user_id:
            metadata["user_id"] = user_id
        
        # Generate vector embedding for the text
        vector = self.embedding_function(text)
        
        # Insert into Milvus
        ids = self.milvus.insert_vectors(
            collection_name=collection_name,
            vectors=[vector],
            texts=[text],
            metadatas=[metadata]
        )
        
        return ids[0] if ids else None
    
    def add_memories(self, texts, metadatas=None, user_id=None, collection_name=None):
        """
        Add multiple memories/documents to the store.
        
        Args:
            texts (list): List of text contents to store
            metadatas (list): List of metadata dicts
            user_id (str): Optional user ID to associate with the memories
            collection_name (str): Optional collection name (defaults to user_memory)
            
        Returns:
            list: IDs of the inserted memories
        """
        if self.embedding_function is None:
            raise ValueError("Embedding function not set")
        
        # Set default collection
        collection_name = collection_name or self.default_collection
        
        # Set default metadatas
        if metadatas is None:
            metadatas = [{} for _ in range(len(texts))]
        
        # Add user_id to all metadatas if provided
        if user_id:
            for metadata in metadatas:
                metadata["user_id"] = user_id
        
        # Generate vector embeddings for all texts
        vectors = [self.embedding_function(text) for text in texts]
        
        # Insert into Milvus
        return self.milvus.insert_vectors(
            collection_name=collection_name,
            vectors=vectors,
            texts=texts,
            metadatas=metadatas
        )
    
    def search_memories(self, query, user_id=None, top_k=5, collection_name=None, cache_ttl=300):
        """
        Search for memories similar to the query.
        
        Args:
            query (str): The query text
            user_id (str): Optional user ID to filter results
            top_k (int): Number of results to return
            collection_name (str): Optional collection name (defaults to user_memory)
            cache_ttl (int): Time to live for cache in seconds (default 5 minutes)
            
        Returns:
            list: List of similar memories
        """
        if self.embedding_function is None:
            raise ValueError("Embedding function not set")
        
        # Set default collection
        collection_name = collection_name or self.default_collection
        
        # Generate cache key
        cache_key = f"memory_search:{collection_name}:{user_id}:{hashlib.md5(query.encode()).hexdigest()}"
        
        # Check cache first
        cached_result = redis_cache.get(cache_key)
        if cached_result:
            print("Using cached memory search result")
            return cached_result
        
        # Perform the search
        results = self.milvus.search_by_text(
            collection_name=collection_name,
            query_text=query,
            embedding_function=self.embedding_function,
            top_k=top_k
        )
        
        # Filter by user_id if provided
        if user_id:
            results = [
                result for result in results 
                if result.get("metadata") and result["metadata"].get("user_id") == user_id
            ]
        
        # Cache the result
        redis_cache.set(cache_key, results, ttl=cache_ttl)
        
        return results
    
    def get_relevant_memories(self, query, user_id=None, top_k=5, collection_name=None):
        """
        Get memories relevant to a query, formatted for use in prompts.
        
        Args:
            query (str): The query text
            user_id (str): Optional user ID to filter results
            top_k (int): Number of results to return
            collection_name (str): Optional collection name (defaults to user_memory)
            
        Returns:
            str: Formatted string of relevant memories for use in prompts
        """
        memories = self.search_memories(
            query=query, 
            user_id=user_id, 
            top_k=top_k, 
            collection_name=collection_name
        )
        
        if not memories:
            return ""
        
        # Format the memories for use in a prompt
        formatted_memories = "Relevant information from memory:\n\n"
        for i, memory in enumerate(memories, 1):
            text = memory.get("text", "")
            formatted_memories += f"{i}. {text}\n\n"
        
        return formatted_memories
    
    def delete_memory(self, memory_id, collection_name=None):
        """
        Delete a memory by ID.
        
        Args:
            memory_id (int): ID of the memory to delete
            collection_name (str): Optional collection name (defaults to user_memory)
            
        Returns:
            bool: True if successful
        """
        # Set default collection
        collection_name = collection_name or self.default_collection
        
        return self.milvus.delete_by_ids(
            collection_name=collection_name,
            ids=[memory_id]
        )
    
    def clear_user_memories(self, user_id, collection_name=None):
        """
        Clear all memories for a specific user.
        This requires a collection with a schema that includes user_id in metadata.
        
        Args:
            user_id (str): User ID whose memories should be cleared
            collection_name (str): Optional collection name (defaults to user_memory)
            
        Returns:
            bool: True if successful
        """
        # Not directly supported by Milvus - would require a custom implementation
        # For now, note that this would be a future enhancement
        raise NotImplementedError("Clearing user memories is not yet implemented")
    
    def get_memory_count(self, user_id=None, collection_name=None):
        """
        Get the count of memories, optionally filtered by user_id.
        
        Args:
            user_id (str): Optional user ID to filter by
            collection_name (str): Optional collection name (defaults to user_memory)
            
        Returns:
            int: Number of memories
        """
        # Set default collection
        collection_name = collection_name or self.default_collection
        
        # For total count
        if user_id is None:
            return self.milvus.get_count(collection_name)
        
        # For user-specific count
        # This requires executing a query, which Milvus doesn't directly support
        # This would be implemented in a future enhancement
        raise NotImplementedError("User-specific memory count is not yet implemented") 