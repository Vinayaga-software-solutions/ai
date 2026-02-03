"""
Ingestion Pipeline Module
Orchestrates the complete ingestion flow: Extract → Clean → Chunk → Embed → Store
Based on DESIGN_KNOWLEDGE.md Data Flow Architecture
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import uuid

from .text_extractor import TextExtractor
from app.chunking import TextCleaner
from app.chunking.chunker import DocumentChunker, TextChunker
from app.embedding.embeddings import BGEEmbeddings
from app.embedding.vector_store import VectorDB
from app.config import settings

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Complete ingestion pipeline for documents.
    
    Flow:
    1. Extract text from file
    2. Clean and preprocess
    3. Chunk into 400-600 token segments
    4. Generate embeddings using BGE
    5. Store in Qdrant with metadata
    """
    
    def __init__(
        self,
        extractor: Optional[TextExtractor] = None,
        chunker: Optional[DocumentChunker] = None,
        embeddings: Optional[BGEEmbeddings] = None,
        vector_store: Optional[VectorDB] = None
    ):
        """
        Initialize the ingestion pipeline.
        
        Args:
            extractor: Text extraction handler
            chunker: Document chunking handler
            embeddings: Embedding generation handler
            vector_store: Vector database handler
        """
        self.extractor = extractor or TextExtractor()
        self.chunker = chunker or DocumentChunker()
        self.embeddings = embeddings or BGEEmbeddings()
        self.vector_store = vector_store or VectorDB()
        self.cleaner = TextCleaner()
    
    def ingest_file(
        self, 
        file_path: str,
        doc_id: Optional[str] = None,
        source: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest a single file through the complete pipeline.
        
        Args:
            file_path: Path to the file to ingest
            doc_id: Optional document ID (auto-generated if not provided)
            source: Source identifier for the document
            additional_metadata: Any additional metadata to attach
            
        Returns:
            Dictionary with ingestion results and statistics
        """
        logger.info(f"Starting ingestion for file: {file_path}")
        
        # Generate doc_id if not provided
        if not doc_id:
            doc_id = self._generate_doc_id(file_path)
        
        # Use file_path as source if not provided
        if not source:
            source = file_path
        
        try:
            # Step 1: Extract text
            extraction_result = self.extractor.extract(file_path)
            
            if not extraction_result["success"]:
                return {
                    "success": False,
                    "error": extraction_result.get("error", "Extraction failed"),
                    "doc_id": doc_id
                }
            
            raw_text = extraction_result["text"]
            file_metadata = extraction_result["metadata"]
            
            logger.info(f"Extracted {len(raw_text)} characters from {file_path}")
            
            # Step 2: Clean text
            cleaned_text = self.cleaner.clean(raw_text)
            logger.info(f"Cleaned text: {len(cleaned_text)} characters")
            
            # Step 3: Chunk document
            metadata = {
                "timestamp": datetime.utcnow().isoformat(),
                **file_metadata,
                **(additional_metadata or {})
            }
            
            chunks = self.chunker.chunk_document(
                text=cleaned_text,
                doc_id=doc_id,
                source=source,
                metadata=metadata
            )
            
            logger.info(f"Created {len(chunks)} chunks")
            
            if not chunks:
                return {
                    "success": False,
                    "error": "No chunks created (document may be too short)",
                    "doc_id": doc_id
                }
            
            # Step 4: Generate embeddings
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embeddings.embed_documents(chunk_texts)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Step 5: Store in Qdrant
            # Generate unique integer IDs for each chunk using UUID to ensure 64-bit unsigned/signed int compatibility
            # Qdrant accepts positive integers or UUID strings. Let's use 64-bit positive ints.
            import uuid
            chunk_ids = []
            for chunk in chunks:
                # Create a deterministic UUID based on the chunk_id string
                u = uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"])
                # distinct integer ID (63-bit positive to be safe)
                chunk_ids.append(u.int & ((1 << 63) - 1))
            
            # Prepare payloads with all metadata
            payloads = []
            for chunk in chunks:
                payload = {
                    "text": chunk["text"],
                    "doc_id": chunk["doc_id"],
                    "chunk_id": chunk["chunk_id"],
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks": chunk["total_chunks"],
                    "token_count": chunk["token_count"],
                    "source": chunk["source"],
                    "timestamp": chunk["timestamp"],
                    "filename": chunk.get("filename", ""),
                    "file_path": chunk.get("file_path", ""),
                }
                
                # Add any additional metadata
                if additional_metadata:
                    for key, value in additional_metadata.items():
                        if key not in payload:
                            payload[key] = value
                
                payloads.append(payload)
            
            logger.info(f"Upserting to Qdrant: {len(chunk_ids)} vectors")
            # Upsert to vector store
            try:
                self.vector_store.upsert(
                    ids=chunk_ids,
                    vectors=embeddings,
                    payloads=payloads
                )
            except Exception as e:
                logger.error(f"Qdrant Upsert failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
                raise e
            
            logger.info(f"Successfully stored {len(chunks)} chunks in Qdrant")
            
            return {
                "success": True,
                "doc_id": doc_id,
                "source": source,
                "chunks_created": len(chunks),
                "total_characters": len(cleaned_text),
                "chunk_ids": [chunk["chunk_id"] for chunk in chunks],
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error during ingestion: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "doc_id": doc_id
            }
    
    def ingest_text(
        self,
        text: str,
        doc_id: Optional[str] = None,
        source: str = "direct_text",
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delegate ingestion of raw text to the ingestion microservice.
        """
        logger.info(f"Delegating ingestion to ingestion-service ({len(text)} characters)")

        if not doc_id:
            doc_id = f"text_{uuid.uuid4().hex[:8]}"

        payload = {"text": text, "doc_id": doc_id, "source": source}
        try:
            import requests
            ingestion_host = getattr(settings, "INGESTION_HOST", "ingestion")
            ingestion_port = getattr(settings, "INGESTION_PORT", 80)
            url = f"http://{ingestion_host}:{ingestion_port}/ingest/text"
            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Delegated ingestion failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "doc_id": doc_id}

    def ingest_file(
        self,
        file_path: str,
        doc_id: Optional[str] = None,
        source: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ingest a single file by extracting its text and delegating to the ingestion service."""
        logger.info(f"Starting file ingestion for: {file_path}")
        if not doc_id:
            doc_id = self._generate_doc_id(file_path)
        if not source:
            source = file_path
        try:
            extraction_result = self.extractor.extract(file_path)
            if not extraction_result.get("success"):
                return {"success": False, "error": extraction_result.get("error", "extraction failed"), "doc_id": doc_id}
            text = extraction_result.get("text", "")
            return self.ingest_text(text, doc_id=doc_id, source=source, additional_metadata=additional_metadata)
        except Exception as e:
            logger.error(f"Error during file ingestion delegation: {e}", exc_info=True)
            return {"success": False, "error": str(e), "doc_id": doc_id}    
    def ingest_batch(
        self,
        file_paths: List[str],
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest multiple files in batch.
        
        Args:
            file_paths: List of file paths to ingest
            additional_metadata: Metadata to attach to all documents
            
        Returns:
            Dictionary with batch ingestion results
        """
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            result = self.ingest_file(file_path, additional_metadata=additional_metadata)
            results.append(result)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        return {
            "total_files": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    def _generate_doc_id(self, file_path: str) -> str:
        """Generate a unique document ID from file path."""
        from pathlib import Path
        filename = Path(file_path).stem
        unique_id = uuid.uuid4().hex[:8]
        return f"{filename}_{unique_id}"
