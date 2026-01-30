# Ingestion Pipeline - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Python 3.10+ (Note: Full pipeline requires Python 3.10-3.12 for fastembed)
- Docker and Docker Compose (for full functionality)
- Git

### Installation

#### Option 1: Local Testing (Core Components Only)

```bash
# Clone the repository
cd c:\Users\vaidh\Documents\ai\gemma-qdrant-rag

# Install minimal dependencies
python -m pip install tiktoken

# Run core component tests
python test_ingestion_simple.py
```

**Output:**
```
🎉 All tests passed!
Total: 5/5 tests passed
```

#### Option 2: Full Pipeline with Docker

```bash
# Start all services
docker-compose up -d

# Install dependencies inside container
docker-compose exec orchestrator pip install -r requirements.txt

# Run full pipeline test
docker-compose exec orchestrator python test_ingestion.py
```

### Quick Examples

#### 1. Ingest a Text File

```bash
# Create a test file
echo "This is a test document about AI and machine learning." > test.txt

# Ingest it
python ingest_cli.py --file test.txt
```

#### 2. Ingest with Custom Metadata

```bash
python ingest_cli.py --file document.txt --doc-id legal_001 --source "Legal Department"
```

#### 3. Ingest Raw Text

```bash
python ingest_cli.py --text "Your important text here that needs to be indexed."
```

#### 4. Batch Ingestion

```bash
python ingest_cli.py --batch file1.txt file2.txt file3.txt
```

### Python API Usage

```python
from app.ingestion_pipeline import IngestionPipeline

# Initialize
pipeline = IngestionPipeline()

# Ingest a file
result = pipeline.ingest_file(
    file_path="document.txt",
    doc_id="doc_001",
    source="my_source",
    additional_metadata={
        "category": "documentation",
        "author": "John Doe",
        "department": "Engineering"
    }
)

# Check result
if result["success"]:
    print(f"✅ Ingested {result['chunks_created']} chunks")
    print(f"Document ID: {result['doc_id']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Understanding the Output

When you ingest a document, you'll see:

```python
{
    "success": True,
    "doc_id": "document_abc123",
    "source": "document.txt",
    "chunks_created": 5,
    "total_characters": 2500,
    "chunk_ids": [
        "document_abc123_chunk_0",
        "document_abc123_chunk_1",
        "document_abc123_chunk_2",
        "document_abc123_chunk_3",
        "document_abc123_chunk_4"
    ],
    "metadata": {
        "timestamp": "2026-01-30T21:49:40.849000",
        "filename": "document.txt",
        "file_path": "/path/to/document.txt",
        "file_size_bytes": 2550,
        ...
    }
}
```

### Verify Ingestion

After ingesting, you can verify the data is in Qdrant:

```python
from app.vector_store import VectorDB
from app.embeddings import BGEEmbeddings

# Initialize
vector_db = VectorDB()
embeddings = BGEEmbeddings()

# Search for something
query = "What is machine learning?"
query_vector = embeddings.embed_query(query)
results = vector_db.search(query_vector, limit=5)

# View results
for result in results:
    print(f"Score: {result.score}")
    print(f"Text: {result.payload['text'][:100]}...")
    print(f"Source: {result.payload['source']}")
    print("---")
```

### Configuration

Edit `app/config.py` to customize:

```python
# Chunking parameters (in chunker.py)
min_tokens = 400
max_tokens = 600
overlap_tokens = 50

# Embedding settings (in config.py)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384

# Vector DB settings (in config.py)
QDRANT_COLLECTION = "rag_collection"
```

### Troubleshooting

#### Issue: "ModuleNotFoundError: No module named 'fastembed'"

**Solution:** Run inside Docker container or use `test_ingestion_simple.py` for core testing.

```bash
docker-compose exec orchestrator python ingest_cli.py --file document.txt
```

#### Issue: "File not found"

**Solution:** Use absolute paths or ensure you're in the correct directory.

```bash
python ingest_cli.py --file "C:\Users\vaidh\Documents\ai\gemma-qdrant-rag\document.txt"
```

#### Issue: "No chunks created"

**Solution:** Document might be too short. Minimum is ~400 tokens (roughly 300 words).

### What Gets Stored?

Each chunk in Qdrant contains:

```json
{
  "text": "The actual chunk text...",
  "doc_id": "document_abc123",
  "chunk_id": "document_abc123_chunk_0",
  "chunk_index": 0,
  "total_chunks": 5,
  "token_count": 487,
  "source": "document.txt",
  "timestamp": "2026-01-30T21:49:40.849000",
  "filename": "document.txt",
  "file_path": "/path/to/document.txt"
}
```

Plus a 384-dimensional embedding vector for semantic search.

### Next Steps

1. **Ingest Your Data**: Start with a few test documents
2. **Test Retrieval**: Query the system to verify chunks are retrievable
3. **Integrate with RAG**: Use the ingested data in your RAG queries
4. **Monitor Performance**: Track ingestion speed and chunk quality
5. **Extend Formats**: Add PDF, JSON support as needed

### Performance Expectations

| File Size | Chunks | Time (Local) | Time (Docker) |
|-----------|--------|--------------|---------------|
| 1 KB      | 1-2    | < 1s         | < 2s          |
| 10 KB     | 5-10   | 1-2s         | 2-3s          |
| 100 KB    | 50-100 | 5-10s        | 10-15s        |
| 1 MB      | 500+   | 30-60s       | 60-120s       |

### Support & Documentation

- **Full Documentation**: `INGESTION_PIPELINE.md`
- **Implementation Summary**: `INGESTION_SUMMARY.md`
- **Design Principles**: `DESIGN_KNOWLEDGE.md`
- **Code Examples**: `test_ingestion_simple.py`

### Common Workflows

#### Workflow 1: Ingest Documentation

```bash
# Ingest all markdown files in a directory
for file in docs/*.md; do
    python ingest_cli.py --file "$file" --source "documentation"
done
```

#### Workflow 2: Update Existing Document

```bash
# Re-ingest with same doc_id to update
python ingest_cli.py --file updated_document.txt --doc-id doc_001
```

#### Workflow 3: Batch Process with Metadata

```python
from app.ingestion_pipeline import IngestionPipeline

pipeline = IngestionPipeline()

files = ["legal_doc1.txt", "legal_doc2.txt", "legal_doc3.txt"]
metadata = {
    "category": "legal",
    "department": "Legal",
    "confidential": True
}

result = pipeline.ingest_batch(files, additional_metadata=metadata)
print(f"Processed {result['successful']}/{result['total_files']} files")
```

---

## 🎯 You're Ready!

Start ingesting your documents and building your private AI knowledge base!

```bash
python ingest_cli.py --file your_document.txt
```

For questions or issues, refer to the full documentation in `INGESTION_PIPELINE.md`.
