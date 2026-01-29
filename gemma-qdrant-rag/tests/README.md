# RAG Test Suite

This directory contains a comprehensive test suite for the Gemma-Qdrant RAG service.

## 📋 Test Case Coverage

The suite includes **20 test cases** across three categories:

1.  **10 Answerable Questions**: Questions based on information about "NovaStream AI" (sample data provided in the suite).
2.  **5 Refusal Questions**: Scenarios where the model should ideally refuse to answer (malicious queries, private data, or out-of-scope requests).
3.  **5 Edge Cases**: Stress tests including empty strings, special characters, long queries, and multilingual input.

## 🚀 How to Run

### 1. Start the RAG Service
Ensure your Docker containers are running:
```powershell
docker-compose up --build
```

### 2. Install Test Dependencies
Since tests run locally, install the required library:
```powershell
python -m pip install -r requirements.txt
```

### 3. Run the Tests
Once the service is healthy, run the test script:
```powershell
python run_tests.py
```

## 📊 Viewing Results
The script will output progress to the console and save a detailed report to `tests/test_results.json`.
