from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Optional, Any
import chromadb
from utils import generate_embedding, rerank_results
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="ChromaDB API")

# Get configuration from environment variables
CHROMA_PATH = os.getenv("CHROMA_PATH", "/chroma/chroma")

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_PATH)

class EmbeddingData(BaseModel):
    documents: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None
    ids: Optional[List[str]] = None

class QueryData(BaseModel):
    query_texts: List[str]
    n_results: int = 10
    where: Optional[Dict[str, Any]] = None
    where_document: Optional[Dict[str, Any]] = None
    rerank: bool = False

class EmbeddingRequest(BaseModel):
    input: str

class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: list
    model: str
    usage: dict

@app.get("/")
async def root():
    return {"message": "ChromaDB API is running", "chroma_path": CHROMA_PATH}

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def embeddings(request: EmbeddingRequest):
    input_text = request.input
    if not input_text:
        raise HTTPException(status_code=400, detail="No input text provided")

    # Generate embeddings
    embeddings = generate_embedding(input_text)

    # Construct the response in OpenAI format
    response = {
        "object": "list",
        "data": [{"object": "embedding", "embedding": embeddings, "index": 0}],
        "model": "BAAI/bge-base-en-v1.5",
        "usage": {
            "prompt_tokens": len(input_text.split()),
            "total_tokens": len(input_text.split()),
        },
    }

    return response

@app.get("/collections")
async def list_collections():
    collections = client.list_collections()
    return {"collections": [coll.name for coll in collections]}

@app.post("/collections/{collection_name}")
async def create_collection(collection_name: str):
    try:
        collection = client.create_collection(name=collection_name)
        return {"message": f"Collection '{collection_name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/collections/{collection_name}")
async def get_collection(collection_name: str):
    try:
        collection = client.get_collection(name=collection_name)
        return {
            "name": collection.name,
            "count": collection.count()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Collection not found: {str(e)}")

@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    try:
        client.delete_collection(name=collection_name)
        return {"message": f"Collection '{collection_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Collection not found: {str(e)}")

@app.post("/collections/{collection_name}/add")
async def add_documents(collection_name: str, data: EmbeddingData):
    try:
        collection = client.get_collection(name=collection_name)
        embeddings = [generate_embedding(embed) for embed in data.documents]
        collection.add(
            documents=data.documents,
            embeddings=embeddings,
            metadatas=data.metadatas,
            ids=data.ids
        )
        return {"message": f"Added {len(data.documents)} documents to collection '{collection_name}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/collections/{collection_name}/query")
async def query_collection(collection_name: str, data: QueryData):
    try:
        collection = client.get_collection(name=collection_name)
        query_embeddings = [generate_embedding(text) for text in data.query_texts]
        
        # Create a query argument dictionary
        query_args = {
            "query_embeddings": query_embeddings,
            "n_results": data.n_results
        }
        
        if data.where and len(data.where) > 0:
            query_args["where"] = data.where
        if data.where_document and len(data.where_document) > 0:
            query_args["where_document"] = data.where_document
            
        results = collection.query(**query_args)
        
        # Apply reranking if requested
        if data.rerank and len(data.query_texts) > 0 and len(results["documents"]) > 0:
            # Flatten results for reranking (assuming single query)
            query = data.query_texts[0]
            documents = results["documents"][0]
            
            # Apply reranking
            if documents:
                reranked_indices = rerank_results(query, documents)
                
                # Reorder all result lists based on new ranking
                for key in results:
                    if isinstance(results[key], list) and len(results[key]) > 0 and len(results[key][0]) > 0:
                        results[key][0] = [results[key][0][i] for i in reranked_indices]
                
                # Add reranking info
                results["reranked"] = True
            
        return results
    except Exception as e:
        import traceback
        print(f"Error during query: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/collections/{collection_name}/peek")
async def peek_collection(collection_name: str, limit: int = 10):
    try:
        collection = client.get_collection(name=collection_name)
        peek_results = collection.peek(limit=limit)
        return peek_results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port) 