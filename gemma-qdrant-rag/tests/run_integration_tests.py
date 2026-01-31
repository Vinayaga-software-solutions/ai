#!/usr/bin/env python3
"""
Run all integration tests in one go.
Requires the RAG API to be running at http://localhost:8000 (e.g. docker-compose up -d).
"""
import os
import sys
import subprocess
import time
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "http://localhost:8000"
WAIT_ATTEMPTS = 30
WAIT_SECONDS = 2

def wait_for_server():
    print(f"Waiting for API at {BASE_URL} (up to {WAIT_ATTEMPTS * WAIT_SECONDS}s)...")
    for i in range(WAIT_ATTEMPTS):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health", timeout=5) as r:
                if r.status == 200:
                    print("API is up.\n")
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(WAIT_SECONDS)
    print("Timeout: API did not become ready. Start the service first (e.g. docker-compose up -d).")
    return False

def main():
    os.chdir(ROOT)
    if not wait_for_server():
        return 1

    tests_dir = os.path.join(ROOT, "tests")
    print("Running integration tests (full suite: ingest + answerable/refusal/edge)...\n")
    result = subprocess.run(
        [sys.executable, "run_tests.py"],
        cwd=tests_dir,
    )
    if result.returncode != 0:
        print("\nIntegration tests failed.")
        return 1
    print("\nAll integration tests passed. Results in tests/test_results.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
