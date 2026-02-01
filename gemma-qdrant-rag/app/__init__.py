# Backward-compatibility re-exports (prefer app.embedding, app.ingestion, app.chunking, app.retrieval)
from app.embedding import BGEEmbeddings, VectorDB
from app.retrieval import GemmaLLM
from app.ingestion import IngestionPipeline, TextExtractor, get_document_storage
from app.chunking import DocumentChunker, TextChunker, TextCleaner

__all__ = [
    "BGEEmbeddings",
    "VectorDB",
    "GemmaLLM",
    "IngestionPipeline",
    "TextExtractor",
    "get_document_storage",
    "DocumentChunker",
    "TextChunker",
    "TextCleaner",
]
