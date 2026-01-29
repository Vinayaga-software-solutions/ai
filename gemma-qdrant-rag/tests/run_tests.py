import requests
import time
import json
from test_data import SAMPLE_DATA, ANSWERABLE_QUESTIONS, REFUSAL_QUESTIONS, EDGE_QUESTIONS

BASE_URL = "http://localhost:8000"

def wait_for_server():
    print("Waiting for API server to be ready...")
    for _ in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("Server is up!")
                return True
        except:
            pass
        time.sleep(2)
    print("Server timeout.")
    return False

def ingest_data():
    print("\n--- Ingesting Sample Data ---")
    for text in SAMPLE_DATA:
        try:
            resp = requests.post(f"{BASE_URL}/ingest", json={"text": text})
            if resp.status_code == 200:
                print(f"Success: {text[:50]}...")
            else:
                print(f"Failed to ingest: {text[:50]} - {resp.text}")
        except Exception as e:
            print(f"Error ingesting: {str(e)}")

def run_test_set(name, questions):
    print(f"\n--- Running {name} ---")
    results = []
    for q in questions:
        print(f"Testing Question: '{q}'")
        try:
            resp = requests.post(f"{BASE_URL}/query", json={"question": q}, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("answer", "No answer found")
                print(f"Answer: {answer[:100]}...")
                results.append({"question": q, "answer": answer, "status": "ok"})
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
                results.append({"question": q, "error": resp.text, "status": "error"})
        except Exception as e:
            print(f"Exception: {str(e)}")
            results.append({"question": q, "exception": str(e), "status": "exception"})
    return results

def main():
    if not wait_for_server():
        return

    ingest_data()
    
    # Give some time for indexing if needed (though Qdrant is usually fast)
    time.sleep(2)

    all_results = {}
    all_results["answerable"] = run_test_set("10 Answerable Questions", ANSWERABLE_QUESTIONS)
    all_results["refusal"] = run_test_set("5 Refusal Questions", REFUSAL_QUESTIONS)
    all_results["edge"] = run_test_set("5 Edge Questions", EDGE_QUESTIONS)

    # Save results to a file
    with open("test_results.json", "w") as f:
        json.dump(all_results, f, indent=4)
    
    print("\n--- Testing Complete ---")
    print("Results saved to 'test_results.json'")

if __name__ == "__main__":
    main()
