import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

API_URL = "http://localhost:8000/query"

def ask_question(question):
    print(f"\n❓ Question: {question}")
    try:
        response = requests.post(API_URL, json={"question": question})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Answer: {data['answer']}")
            print(f"📚 Sources: {len(data.get('sources', []))}")
            for i, source in enumerate(data.get('sources', [])[:3]):
                name = source.get('source', 'Unknown')
                text_preview = source.get('text', '')[:50].replace('\n', ' ')
                score = source.get('score', 'N/A')
                # Format score if it's a number
                if isinstance(score, float):
                    score_str = f"{score:.3f}"
                else:
                    score_str = str(score)
                print(f"   {i+1}. [{name}] (Score: {score_str}) \"{text_preview}...\"")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Failed to call API: {e}")

if __name__ == "__main__":
    # Question specific to the ingested document content

    ask_question("What is RAG?")
    ask_question("What are the key components of a RAG system?")
    ask_question("What is the optimal chunk size range?")
    ask_question("Why is metadata important?")
    ask_question("What are the important features of vector databases?")
    ask_question("Who invented RAG?")
    ask_question("What dimensionality do embedding models typically have?")


    # ask_question("What is the optimal chunk size range and why?")
    # ask_question("Why is chunking important in RAG systems?")
    # ask_question("Why is metadata important?")
    # ask_question("What information should metadata contain?")
    # ask_question("What are embedding models used for?")
    # ask_question("What dimensionality do embedding models typically have?")
    # ask_question("What are the important features of vector databases?")
    # ask_question("Which similarity metrics do vector databases support?")
    # ask_question("How does metadata help with governance and auditability?")
    # ask_question("What are some hallucination defense techniques?")
    # ask_question("What is retrieval confidence threshold?")
    # ask_question("What future enhancements are suggested for the ingestion pipeline?")
    # ask_question("Why should raw data not be directly used by AI systems?")

