import chromadb
import os

# Ensure database folder exists
os.makedirs("./database/chroma_db", exist_ok=True)

# Create persistent client
client = chromadb.PersistentClient(
    path="./database/chroma_db"
)

# Create collection
collection = client.get_or_create_collection(
    name="cv_collection"
)

def store_cv(cv_id, cv_text, embedding):

    collection.add(
        ids=[cv_id],
        documents=[cv_text],
        embeddings=[embedding.tolist()]
    )

def search_similar_cvs(job_embedding):

    results = collection.query(
        query_embeddings=[job_embedding.tolist()],
        n_results=3
    )

    return results