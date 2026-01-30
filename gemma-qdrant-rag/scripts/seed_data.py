import os
import requests
import time

BASE_URL = os.getenv("API_URL", "http://localhost:8000")

def init_db():
    sample_data = [
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
