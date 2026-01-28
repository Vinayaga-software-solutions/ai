import requests
import time

BASE_URL = "http://localhost:8000"

def init_db():
    sample_data = [
        "Gemma is a family of lightweight, state-of-the-art open models from Google, built from the same technology used to create the Gemini models.",
        "Qdrant is a vector similarity search engine. It provides a production-ready service with a convenient API to store, search, and manage points - vectors with an additional payload.",
        "BGE (BAAI General Embedding) is a highly efficient embedding model that performs well on retrieval tasks.",
        "RAG stands for Retrieval-Augmented Generation, a technique to provide LLMs with specific context data."
    ]

    print("Checking if API is up...")
    max_retries = 5
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health")
            break
        except:
            print(f"Waiting for server... ({i+1}/{max_retries})")
            time.sleep(2)

    for text in sample_data:
        print(f"Ingesting: {text[:50]}...")
        resp = requests.post(f"{BASE_URL}/ingest", json={"text": text})
        print(f"Status: {resp.status_code}")

if __name__ == "__main__":
    init_db()
