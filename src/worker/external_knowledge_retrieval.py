from chroma.services.embedder import Embedder
from chroma.utils import generate_embedding
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
    
def search_knowledge(user_information: dict):
    # format user information

    # search aspects for user information : google_search(question)

    # return search result -> knowledges

    pass


def store_knowledge(knowledges):
    embedder = Embedder()
    # embedder.generate_embedding(knowledges)

    """
    add_documents(
        collection_name="knowledge",
        data=embedder
    )
    """
    pass


if __name__ == "__main__":
    user_information = {
        "name":"tuan anh",
        "age":20,
        "job": "data scientist"
    }
    store_knowledge(search_knowledge(
        user_information=user_information
    ))

