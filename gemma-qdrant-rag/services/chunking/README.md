# Chunking Service (skeleton)

A minimal FastAPI service that will eventually handle preprocessing, summaries, and chunk splitting.

Endpoints:
- GET /health — health check
- GET /summarize — placeholder
- POST /chunk — token-based chunking (plain text)
- POST /chunk/tree — tree-aware chunking with document type + semantic mapping

Run with Docker (from repo root):

```bash
docker compose up --build
```

Tree-aware chunking example:

```bash
curl -X POST http://localhost:8011/chunk/tree \
  -H "Content-Type: application/json" \
  -d '{
    "text": "# Title\nThis is **bold** text with a [link](https://example.com).",
    "doc_id": "doc_001",
    "source": "demo",
    "doc_type": "markdown",
    "semantic_mapping": {
      "bold": {"signal": "key_term", "weight": 2.0},
      "italic": {"signal": "secondary", "weight": 0.5},
      "link": {"signal": "citation", "weight": 1.0},
      "heading": {"signal": "section", "weight": 1.0}
    }
  }'
```

Relationship metadata:
- `heading_path` provides the full path of headings for a chunk.
- `parent_section` captures the immediate parent heading (if any).
- `section_hierarchy` includes heading titles and levels for the subtree lineage.
