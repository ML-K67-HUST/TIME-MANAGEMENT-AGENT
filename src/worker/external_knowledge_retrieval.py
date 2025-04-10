from chroma.services.embedder import Embedder
from chroma.utils import generate_embedding
from utlis import google_search
from database import vectordb
import chromadb
import os

CHROMA_PATH = os.getenv("CHROMA_PATH", "/chroma/chroma")


# this is Hieu's work

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_PATH)


def add_documents(collection_name: str, data):
    collection = client.get_collection(name=collection_name)
    embeddings = [generate_embedding(embed) for embed in data.documents]
    collection.add(
        documents=data.documents,
        embeddings=embeddings,
        metadatas=data.metadatas,
        ids=data.ids
    )
    return {"message": f"Added {len(data.documents)} documents to collection '{collection_name}'"}

#khai bao mang knowledges va user_information
knowledges = []
user_information = {}

def return_question(user_information:dict):
    job = user_information.get("job", "professional")
    questions = [
        f"What are the latest trends in {job}?",
        f"What tools should a {job} master in 2024?",
        f"What are common challenges faced by a {job}?",
        f"What online resources or communities are valuable for a {job}?",
        f"What productivity techniques help a {job} succeed?"
    ]
    return questions

def search_knowledge(user_information: dict):
    # format user information

    # search aspects for user information : google_search(question)

    # return search result -> knowledges

    job = user_information.get("job", "professional")

    questions = [
        f"What are the latest trends in {job}?",
        f"What tools should a {job} master in 2024?",
        f"What are common challenges faced by a {job}?",
        f"What online resources or communities are valuable for a {job}?",
        f"What productivity techniques help a {job} succeed?"
    ]

    
    for question in questions:
        search_results = google_search(question)
        if search_results:
            knowledges.append({
                "question": question,
                "results": search_results
            })

    return knowledges



import requests

def chunk_text(text, chunk_size=300):
    """
    Splits text into smaller chunks.
    """
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

chunks = chunk_text(" ".join([knowledge["results"] for knowledge in knowledges]), chunk_size=300)
question = return_question(user_information)

def store_knowledge(knowledges):
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    }

    params = {
        'vector_store': 'milvus',
    }

    json_data = {
        'documents':  chunks,
        'metadatas': [question]*len(chunks),
    }
    collection_name = "knowledge_user"
    response = requests.post(
        f'https://timenest-vector-store-production.up.railway.app/collections/{collection_name}/add',
        params=params,
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        print("successfull")



if __name__ == "__main__":
    user_information = {
        "name":"tuan anh",
        "age":20,
        "job": "data scientist"
    }
    store_knowledge(search_knowledge(
        user_information=user_information
    ))

