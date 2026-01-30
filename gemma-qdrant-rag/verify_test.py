import requests
from qdrant_client import QdrantClient
import os
import sys

def check_embedding():
    url = os.environ.get("EMBEDDING_API_URL", "http://localhost:8081/embed")
    print(f"Checking Embedding Service at {url}...")
    try:
        response = requests.post(url, json={"inputs": ["Hello world"]})
        if response.status_code == 200:
            print(f"✅ Embedding Service OK: {len(response.json()[0])} dims")
        else:
            print(f"❌ Embedding Service Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Embedding Service Failed: {e}")

def check_qdrant():
    host = os.environ.get("QDRANT_HOST", "localhost")
    port = int(os.environ.get("QDRANT_PORT", 6333))
    print(f"Checking Qdrant at {host}:{port}...")
    try:
        client = QdrantClient(host=host, port=port)
        collections = client.get_collections()
        print(f"✅ Qdrant OK. Collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"❌ Qdrant Failed: {e}")

if __name__ == "__main__":
    check_embedding()
    check_qdrant()
