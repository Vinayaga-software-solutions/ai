import os
import requests
import time

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


def init_db():
    sample_data = [
    ]

    print("Checking if API is up...")
    max_retries = 10
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health")
            break
        except Exception:
            print(f"Waiting for server... ({i+1}/{max_retries})")
            time.sleep(2)

    for text in sample_data:
        print(f"Ingesting: {text[:50]}...")
        try:
            resp = requests.post(f"{BASE_URL}/ingest", json={"text": text})
            print(f"Status: {resp.status_code}")
        except Exception as e:
            print(f"Ingest failed: {e}")

    # If running in Docker Compose with a shared volume, write a completion marker
    state_dir = os.getenv('SEEDER_STATE_PATH', '/state')
    try:
        if os.path.isdir(state_dir):
            with open(os.path.join(state_dir, 'seeder_done'), 'w') as f:
                f.write('done\n')
            print(f"Wrote seeder_done marker to {os.path.join(state_dir, 'seeder_done')}")
    except Exception as e:
        print(f"Could not write seeder marker: {e}")


if __name__ == "__main__":
    init_db()
