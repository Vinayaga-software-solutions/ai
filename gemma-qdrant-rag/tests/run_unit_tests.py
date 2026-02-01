#!/usr/bin/env python3
"""
Run all unit tests in one go.
Unit tests do not require the API or any external services (Qdrant, embedding, LLM).
"""
import os
import sys
import subprocess

# Project root = parent of tests/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

UNIT_TESTS = [
    "tests/test_ingestion_simple.py",
    "tests/test_document_storage.py",
    "tests/test_chunking_service.py",
    "tests/test_ingestion_service.py",
    "tests/test_embedding_service.py",
    "tests/test_retrieval_service.py",
]

def main():
    print("Running all unit tests (no services required)...\n")
    failed = []
    for path in UNIT_TESTS:
        name = path.replace("tests/", "").replace(".py", "")
        print(f"--- {name} ---")
        result = subprocess.run(
            [sys.executable, path],
            cwd=ROOT,
        )
        if result.returncode != 0:
            failed.append(name)
        print()
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print("All unit tests passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
