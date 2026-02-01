#!/usr/bin/env python3
"""
Ingestion CLI Tool
Command-line interface for testing the ingestion pipeline
"""
import argparse
import sys
import logging
from pathlib import Path
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ingestion import IngestionPipeline, TextExtractor, get_document_storage
from app.chunking import DocumentChunker
from app.embedding import BGEEmbeddings, VectorDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_file(file_path: str, doc_id: str = None, source: str = None):
    """Ingest a single file and save it to configured storage (local folder or GCS)."""
    logger.info(f"Initializing ingestion pipeline...")
    pipeline = IngestionPipeline()
    storage = get_document_storage()

    logger.info(f"Ingesting file: {file_path}")
    result = pipeline.ingest_file(
        file_path=file_path,
        doc_id=doc_id,
        source=source
    )

    if result["success"]:
        try:
            saved_path = storage.save_file(file_path, result["doc_id"])
            logger.info(f"Document saved to storage: {saved_path}")
        except Exception as e:
            logger.warning(f"Storage save failed (ingestion succeeded): {e}")
        logger.info("✅ Ingestion successful!")
        logger.info(f"Document ID: {result['doc_id']}")
        logger.info(f"Source: {result['source']}")
        logger.info(f"Chunks created: {result['chunks_created']}")
        logger.info(f"Total characters: {result['total_characters']}")
        logger.info(f"Chunk IDs: {', '.join(result['chunk_ids'][:5])}{'...' if len(result['chunk_ids']) > 5 else ''}")
    else:
        logger.error(f"❌ Ingestion failed: {result['error']}")
        sys.exit(1)


def ingest_text(text: str, doc_id: str = None, source: str = "cli"):
    """Ingest raw text and save it to configured storage (local folder or GCS)."""
    logger.info(f"Initializing ingestion pipeline...")
    pipeline = IngestionPipeline()
    storage = get_document_storage()

    logger.info(f"Ingesting text ({len(text)} characters)...")
    result = pipeline.ingest_text(
        text=text,
        doc_id=doc_id,
        source=source
    )

    if result["success"]:
        try:
            filename = f"doc_{result['doc_id']}.txt"
            saved_path = storage.save_content(text.encode("utf-8"), filename, result["doc_id"])
            logger.info(f"Document saved to storage: {saved_path}")
        except Exception as e:
            logger.warning(f"Storage save failed (ingestion succeeded): {e}")
        logger.info("✅ Ingestion successful!")
        logger.info(f"Document ID: {result['doc_id']}")
        logger.info(f"Chunks created: {result['chunks_created']}")
        logger.info(f"Total characters: {result['total_characters']}")
    else:
        logger.error(f"❌ Ingestion failed: {result['error']}")
        sys.exit(1)


def ingest_batch(file_paths: list):
    """Ingest multiple files and save each to configured storage (local folder or GCS)."""
    logger.info(f"Initializing ingestion pipeline...")
    pipeline = IngestionPipeline()
    storage = get_document_storage()

    logger.info(f"Ingesting {len(file_paths)} files...")
    result = pipeline.ingest_batch(file_paths)

    for i, r in enumerate(result["results"]):
        if r.get("success") and i < len(file_paths):
            try:
                saved_path = storage.save_file(file_paths[i], r.get("doc_id"))
                logger.info(f"Saved to storage: {saved_path}")
            except Exception as e:
                logger.warning(f"Storage save failed for {file_paths[i]}: {e}")

    logger.info(f"✅ Batch ingestion complete!")
    logger.info(f"Total files: {result['total_files']}")
    logger.info(f"Successful: {result['successful']}")
    logger.info(f"Failed: {result['failed']}")

    if result["failed"] > 0:
        logger.warning("Failed files:")
        for r in result["results"]:
            if not r["success"]:
                logger.warning(f"  - {r.get('doc_id', 'unknown')}: {r.get('error', 'unknown error')}")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest documents into the RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest a single file
  python ingest_cli.py --file document.txt
  
  # Ingest with custom doc_id
  python ingest_cli.py --file document.txt --doc-id my_doc_001
  
  # Ingest raw text
  python ingest_cli.py --text "This is some text to ingest"
  
  # Ingest multiple files
  python ingest_cli.py --batch file1.txt file2.txt file3.txt
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file', '-f',
        type=str,
        help='Path to a single file to ingest'
    )
    input_group.add_argument(
        '--text', '-t',
        type=str,
        help='Raw text to ingest'
    )
    input_group.add_argument(
        '--batch', '-b',
        nargs='+',
        help='Multiple files to ingest in batch'
    )
    
    # Optional parameters
    parser.add_argument(
        '--doc-id',
        type=str,
        help='Custom document ID (auto-generated if not provided)'
    )
    parser.add_argument(
        '--source',
        type=str,
        help='Source identifier for the document'
    )
    
    args = parser.parse_args()
    
    try:
        if args.file:
            ingest_file(args.file, args.doc_id, args.source)
        elif args.text:
            ingest_text(args.text, args.doc_id, args.source)
        elif args.batch:
            ingest_batch(args.batch)
    except KeyboardInterrupt:
        logger.info("\nIngestion cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
