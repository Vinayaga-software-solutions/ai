# Ingestion Pipeline

A production-ready ingestion pipeline for the Private AI Governance System, implementing the data flow architecture from `DESIGN_KNOWLEDGE.md`.

## Overview

The ingestion pipeline processes documents through the following stages:

```
Extract → Clean → Chunk → Embed → Store
```

### Pipeline Flow

1. **Extract Text** - Extract text from files (TXT, MD, future: PDF, JSON)
2. **Clean** - Remove noise, normalize whitespace, handle encoding
3. **Chunk** - Split into 400-600 token segments with overlap
4. **Generate Embeddings** - Create vector embeddings using BGE
5. **Store in Qdrant** - Save embeddings with rich metadata

## Architecture

### Components

#### 1. Text Extractor (`text_extractor.py`)
- Extracts text from various file formats
- Currently supports: `.txt`, `.md`
- Extensible for: `.pdf`, `.json`, `.csv`
- Captures file metadata (size, timestamps, path)

#### 2. Text Cleaner (`text_extractor.py`)
- Removes null bytes and control characters
- Normalizes line endings
- Removes excessive whitespace
- Preserves semantic structure

#### 3. Text Chunker (`chunker.py`)
- Token-based chunking (400-600 tokens)
- Sentence-aware splitting for semantic boundaries
- Configurable overlap between chunks
- Uses tiktoken for accurate token counting

#### 4. Document Chunker (`chunker.py`)
- Document-level orchestration
- Metadata propagation
- Chunk ID generation
- Position tracking

#### 5. Ingestion Pipeline (`ingestion_pipeline.py`)
- Orchestrates the complete flow
- Handles errors gracefully
- Supports batch processing
- Generates comprehensive metadata

## Metadata Schema

Each chunk is stored with the following metadata:

```python
{
    "text": str,              # The chunk text
    "doc_id": str,            # Document identifier
    "chunk_id": str,          # Unique chunk identifier
    "chunk_index": int,       # Position in document
    "total_chunks": int,      # Total chunks in document
    "token_count": int,       # Number of tokens in chunk
    "source": str,            # Source identifier
    "timestamp": str,         # ISO format timestamp
    "filename": str,          # Original filename
    "file_path": str,         # Full file path
    # ... additional custom metadata
}
```

## Usage

### 1. Command Line Interface

```bash
# Install dependencies
pip install -r requirements.txt

# Ingest a single file
python ingest_cli.py --file document.txt

# Ingest with custom doc_id
python ingest_cli.py --file document.txt --doc-id my_doc_001

# Ingest raw text
python ingest_cli.py --text "This is some text to ingest"

# Batch ingestion
python ingest_cli.py --batch file1.txt file2.txt file3.txt
```

### 2. Python API

```python
from app.ingestion_pipeline import IngestionPipeline

# Initialize pipeline
pipeline = IngestionPipeline()

# Ingest a file
result = pipeline.ingest_file(
    file_path="document.txt",
    doc_id="doc_001",
    source="my_source",
    additional_metadata={"category": "legal", "author": "John Doe"}
)

# Ingest raw text
result = pipeline.ingest_text(
    text="Your text here...",
    doc_id="text_001",
    source="api",
    additional_metadata={"type": "user_input"}
)

# Batch ingestion
result = pipeline.ingest_batch(
    file_paths=["file1.txt", "file2.txt"],
    additional_metadata={"batch_id": "batch_001"}
)
```

### 3. Custom Configuration

```python
from app.ingestion_pipeline import IngestionPipeline
from app.chunker import TextChunker, DocumentChunker

# Custom chunking parameters
custom_chunker = DocumentChunker(
    token_chunker=TextChunker(
        min_tokens=300,
        max_tokens=500,
        overlap_tokens=75
    )
)

# Initialize with custom components
pipeline = IngestionPipeline(chunker=custom_chunker)
```

## Testing

Run the comprehensive test suite:

```bash
python test_ingestion.py
```

This tests:
- Text extraction
- Text cleaning
- Token-based chunking
- Document chunking with metadata
- Full pipeline integration
- Direct text ingestion

## Configuration

The pipeline uses settings from `app/config.py`:

```python
# Embedding settings
EMBEDDING_STRATEGY: str = "local"
EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM: int = 384

# Vector DB settings
QDRANT_HOST: str = "qdrant"
QDRANT_PORT: int = 6333
QDRANT_COLLECTION: str = "rag_collection"
```

## Chunking Strategy

Based on `DESIGN_KNOWLEDGE.md` - Section: Chunking Strategies

### Token-Based Chunking (400-600 tokens)

**Why this range?**
- **Minimum 400 tokens**: Ensures sufficient context for semantic understanding
- **Maximum 600 tokens**: Prevents noise and maintains retrieval precision
- **Overlap (50 tokens)**: Maintains semantic continuity across chunks

### Sentence-Aware Splitting

The chunker respects sentence boundaries to avoid cutting mid-sentence, which:
- Preserves semantic meaning
- Improves embedding quality
- Enhances retrieval accuracy

### Long Sentence Handling

If a single sentence exceeds max_tokens:
- Split at word boundaries
- Maintain readability
- Preserve as much context as possible

## Future Enhancements

### Planned File Format Support

1. **PDF Documents**
   ```python
   # Will use PyPDF2 or pdfplumber
   SUPPORTED_FORMATS['.pdf'] = 'pdf'
   ```

2. **JSON Data**
   ```python
   # Structured data extraction
   SUPPORTED_FORMATS['.json'] = 'json'
   ```

3. **CSV/Tabular Data**
   ```python
   # Table-aware chunking
   SUPPORTED_FORMATS['.csv'] = 'csv'
   ```

### Advanced Features

- **Incremental Updates**: Update existing documents without re-ingesting
- **Deduplication**: Detect and handle duplicate content
- **Multi-language Support**: Language-specific chunking and cleaning
- **Quality Scoring**: Assess chunk quality before storage
- **Automated Summarization**: Generate summaries for each chunk

## Design Principles

Following `DESIGN_KNOWLEDGE.md`:

1. **Metadata-First**: Rich metadata for governance and auditability
2. **Deterministic**: Same input always produces same output
3. **Extensible**: Easy to add new file formats and processors
4. **Testable**: Comprehensive test coverage
5. **Production-Ready**: Error handling, logging, validation

## Integration with RAG System

The ingestion pipeline integrates seamlessly with the RAG query flow:

```
Ingestion: File → Extract → Clean → Chunk → Embed → Store
Query:     Question → Embed → Search → Retrieve → Generate → Answer
```

Both use the same:
- Embedding model (BGE)
- Vector database (Qdrant)
- Metadata schema
- Configuration

This ensures consistency and accuracy in retrieval.

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure you're in the correct directory
cd gemma-qdrant-rag
python test_ingestion.py
```

**2. Qdrant Connection Issues**
```bash
# Start Qdrant with Docker
docker-compose up -d qdrant
```

**3. Encoding Errors**
```python
# Specify encoding explicitly
result = extractor.extract("file.txt", encoding='utf-8')
```

**4. Token Count Issues**
```bash
# Install tiktoken
pip install tiktoken
```

## Performance Considerations

### Chunking Performance
- **Small files (<100KB)**: Instant
- **Medium files (100KB-1MB)**: 1-5 seconds
- **Large files (>1MB)**: 5-30 seconds

### Embedding Generation
- **Local (fastembed)**: ~100-500 chunks/second
- **Remote API**: Depends on network and service

### Storage
- **Qdrant upsert**: ~1000-5000 vectors/second

## License

Part of the Private AI Governance System project.
