# Backward-compatibility re-exports (prefer app.embedding, app.ingestion, app.chunking, app.retrieval)
from app.embedding import BGEEmbeddings, VectorDB
from app.retrieval import GemmaLLM
from app.ingestion import IngestionPipeline, TextExtractor, get_document_storage
from app.chunking import DocumentChunker, TextCleaner

# TextChunker is an optional local implementation that depends on `tiktoken`.
# Import it lazily so the orchestrator can start without the optional native
# dependency (we encourage using the chunking microservice instead).
try:
    from app.chunking.chunker import TextChunker
except Exception:
    TextChunker = None

__all__ = [
    "BGEEmbeddings",
    "VectorDB",
    "GemmaLLM",
    "IngestionPipeline",
    "TextExtractor",
    "get_document_storage",
    "DocumentChunker",
    "TextCleaner",
]

if TextChunker is not None:
    __all__.append("TextChunker")
