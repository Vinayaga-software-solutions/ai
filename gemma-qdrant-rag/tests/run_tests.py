import os
import sys
import requests
import time
import json
import sys
import os
# Ensure local services are used when running tests outside Docker (allow overrides from CI/env)
os.environ.setdefault("QDRANT_HOST", "localhost")
os.environ.setdefault("QDRANT_PORT", "6333")
os.environ.setdefault("QDRANT_COLLECTION", "local_rag")
os.environ.setdefault("EMBEDDING_STRATEGY", "remote")
os.environ.setdefault("EMBEDDING_API_URL", "http://localhost:8081/embed")
from test_data import SAMPLE_DATA, ANSWERABLE_QUESTIONS, REFUSAL_QUESTIONS, EDGE_QUESTIONS

# Ensure project root is on sys.path so imports like `app.ingestion` work when running from tests/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
    print("\n--- Ingesting Sample Data via IngestionPipeline ---")
    # Use the real ingestion pipeline (chunking, metadata, embeddings, storage)
    try:
        from app.ingestion import IngestionPipeline
    except Exception as e:
        print(f"Failed to import IngestionPipeline, falling back to HTTP ingest: {e}")
        for text in SAMPLE_DATA:
            try:
                resp = requests.post(f"{BASE_URL}/ingest", json={"text": text})
                if resp.status_code == 200:
                    print(f"Success (http): {text[:50]}...")
                else:
                    print(f"Failed to ingest (http): {text[:50]} - {resp.text}")
            except Exception as e:
                print(f"Error ingesting (http): {str(e)}")
        return

    pipeline = IngestionPipeline()

    # Combine all sample texts into a larger single document so chunking produces multiple chunks
    combined_text = "\n\n".join(SAMPLE_DATA * 6)
    try:
        result = pipeline.ingest_text(combined_text, doc_id="itest_full", source="integration_test")
        if result.get("success"):
            print(f"Success (pipeline): combined document -> {result.get('doc_id')} (chunks: {result.get('chunks_created')})")
        else:
            print(f"Failed to ingest combined document: {result.get('error')}")
            # Fallback: try ingesting items individually (best-effort)
            for i, text in enumerate(SAMPLE_DATA):
                try:
                    r = pipeline.ingest_text(text, doc_id=f"itest_{i}", source="integration_test")
                    if r.get("success"):
                        print(f"Success (pipeline single): {r.get('doc_id')}")
                    else:
                        print(f"Failed single ingest: {text[:50]} - {r.get('error')}")
                except Exception as e:
                    print(f"Error ingesting single: {str(e)}")
    except Exception as e:
        print(f"Error ingesting combined document: {e}")

    # Allow time for indexing if needed
    time.sleep(1)

    # Verify that at least one point contains chunk metadata (doc_id/chunk_id)
    try:
        resp = requests.post(f"http://localhost:6333/collections/local_rag/points/scroll", json={"limit":10, "with_payload":True, "with_vector":False}, timeout=10)
        points = resp.json().get("result", {}).get("points", [])
        has_meta = any(p.get("payload", {}).get("doc_id") or p.get("payload", {}).get("chunk_id") for p in points)
        if has_meta:
            print("Verification: chunk metadata present in Qdrant points.")
        else:
            print("ERROR: no chunk metadata found in Qdrant points. Dumping sample points for debugging:")
            print(f"Total points returned: {len(points)}")
            for i, p in enumerate(points[:5]):
                print(f"Point {i}: id={p.get('id')}, payload keys={list(p.get('payload', {}).keys())}")
            print("Sample payloads:")
            print(json.dumps(points[:5], indent=2))
            sys.exit(1)
    except Exception as e:
        print(f"Could not verify Qdrant points: {e}")

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
