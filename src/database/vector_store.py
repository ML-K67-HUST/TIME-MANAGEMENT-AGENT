import os
import time
import numpy as np
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)
from config import settings

class MilvusClient:
    """
    A client for interacting with Milvus vector database.
    Handles common operations like creating collections, inserting vectors,
    searching by similarity, and managing indices.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MilvusClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host=None, port=None):
        if self._initialized:
            return
            
        self.host = host or os.getenv("MILVUS_HOST", "localhost")
        self.port = port or os.getenv("MILVUS_PORT", "19530")
        self._connect()
        self._initialized = True

    def _connect(self):
        """Connect to Milvus server"""
        try:
            connections.connect(
                alias="default", 
                host=self.host, 
                port=self.port
            )
            print(f"Connected to Milvus server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Milvus: {str(e)}")
            raise

    def create_collection(self, collection_name, dim=1536, description=None):
        """
        Create a new collection in Milvus.
        
        Args:
            collection_name (str): Name of the collection
            dim (int): Dimension of the vectors (default is 1536 for OpenAI embeddings)
            description (str): Optional description of the collection
            
        Returns:
            Collection: The created collection
        """
        if utility.has_collection(collection_name):
            print(f"Collection {collection_name} already exists")
            return Collection(collection_name)
        
        # Define fields for the collection
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="created_at", dtype=DataType.INT64)
        ]
        
        # Create collection schema
        schema = CollectionSchema(fields=fields, description=description)
        
        # Create collection
        collection = Collection(name=collection_name, schema=schema)
        
        # Create an IVF_FLAT index for the vector field
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="vector", index_params=index_params)
        
        print(f"Created collection: {collection_name}")
        return collection

    def get_collection(self, collection_name):
        """
        Get a collection by name.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            Collection: The requested collection or None if it doesn't exist
        """
        if not utility.has_collection(collection_name):
            print(f"Collection {collection_name} does not exist")
            return None
            
        return Collection(collection_name)

    def list_collections(self):
        """
        List all collections in the database.
        
        Returns:
            list: List of collection names
        """
        return utility.list_collections()

    def drop_collection(self, collection_name):
        """
        Drop a collection.
        
        Args:
            collection_name (str): Name of the collection to drop
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not utility.has_collection(collection_name):
            print(f"Collection {collection_name} does not exist")
            return False
            
        utility.drop_collection(collection_name)
        print(f"Dropped collection: {collection_name}")
        return True

    def insert_vectors(self, collection_name, vectors, texts, metadatas=None):
        """
        Insert vectors into a collection.
        
        Args:
            collection_name (str): Name of the collection
            vectors (list): List of vectors to insert
            texts (list): List of text associated with the vectors
            metadatas (list): List of metadata dicts (optional)
            
        Returns:
            list: List of inserted IDs
        """
        collection = self.get_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection {collection_name} does not exist")
        
        if len(vectors) != len(texts):
            raise ValueError("Number of vectors and texts must match")
            
        if metadatas is None:
            metadatas = [{} for _ in range(len(vectors))]
        
        # Prepare data for insertion
        entities = [
            vectors,
            texts,
            metadatas,
            [int(time.time() * 1000) for _ in range(len(vectors))]
        ]
        
        # Insert data
        insert_result = collection.insert(entities)
        
        # Return the inserted IDs
        return insert_result.primary_keys

    def search_by_vector(self, collection_name, query_vector, top_k=10, output_fields=None):
        """
        Search for similar vectors in a collection.
        
        Args:
            collection_name (str): Name of the collection
            query_vector (list): The query vector
            top_k (int): Number of results to return
            output_fields (list): Additional fields to return besides the vector
            
        Returns:
            list: List of search results
        """
        collection = self.get_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection {collection_name} does not exist")
        
        # Load collection
        collection.load()
        
        # Set default output fields if not provided
        if output_fields is None:
            output_fields = ["text", "metadata"]
            
        # Add any missing essential fields
        if "text" not in output_fields:
            output_fields.append("text")
        if "metadata" not in output_fields:
            output_fields.append("metadata")
        
        # Prepare search parameters
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        # Execute search
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=output_fields
        )
        
        # Format and return the results
        formatted_results = []
        for hits in results:
            for hit in hits:
                item = {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.entity.get("text")
                }
                # Add metadata if available
                if "metadata" in hit.entity:
                    item["metadata"] = hit.entity.get("metadata")
                
                # Add any other requested fields
                for field in output_fields:
                    if field not in ["text", "metadata"] and field in hit.entity:
                        item[field] = hit.entity.get(field)
                
                formatted_results.append(item)
        
        return formatted_results

    def search_by_text(self, collection_name, query_text, embedding_function, top_k=10, output_fields=None):
        """
        Search for similar text in a collection.
        
        Args:
            collection_name (str): Name of the collection
            query_text (str): The query text
            embedding_function (callable): Function to convert text to vector
            top_k (int): Number of results to return
            output_fields (list): Additional fields to return besides the vector
            
        Returns:
            list: List of search results
        """
        # Convert query text to vector
        query_vector = embedding_function(query_text)
        
        # Search by vector
        return self.search_by_vector(
            collection_name=collection_name,
            query_vector=query_vector,
            top_k=top_k,
            output_fields=output_fields
        )

    def delete_by_ids(self, collection_name, ids):
        """
        Delete vectors by their IDs.
        
        Args:
            collection_name (str): Name of the collection
            ids (list): List of IDs to delete
            
        Returns:
            bool: True if successful
        """
        collection = self.get_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection {collection_name} does not exist")
            
        # Execute deletion
        collection.delete(expr=f"id in {ids}")
        return True

    def get_count(self, collection_name):
        """
        Get the number of entities in a collection.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            int: Number of entities
        """
        collection = self.get_collection(collection_name)
        if collection is None:
            return 0
            
        return collection.num_entities

    def flush_collection(self, collection_name):
        """
        Flush a collection to disk.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            bool: True if successful
        """
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
            
        collection.flush()
        return True
        
    def close(self):
        """Close the connection to Milvus"""
        connections.disconnect("default")
        print("Disconnected from Milvus") 