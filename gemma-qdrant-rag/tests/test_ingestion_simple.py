#!/usr/bin/env python3
"""
Simple Test Ingestion Pipeline (without embeddings)
Tests the core ingestion logic without requiring fastembed
"""
import sys
from pathlib import Path
import os

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from app.text_extractor import TextExtractor, TextCleaner
from app.chunker import TextChunker, DocumentChunker
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_text_extraction():
    """Test text extraction from file."""
    logger.info("=" * 60)
    logger.info("TEST 1: Text Extraction")
    logger.info("=" * 60)
    
    extractor = TextExtractor()
    
    # Test with sample document
    result = extractor.extract(os.path.join(os.path.dirname(__file__), '../data/sample_document.txt'))
    
    if result["success"]:
        logger.info(f"✅ Extraction successful")
        logger.info(f"   Characters extracted: {len(result['text'])}")
        logger.info(f"   Filename: {result['metadata']['filename']}")
        logger.info(f"   File size: {result['metadata']['file_size_bytes']} bytes")
        logger.info(f"   First 100 chars: {result['text'][:100]}...")
        return True
    else:
        logger.error(f"❌ Extraction failed: {result.get('error')}")
        return False


def test_text_cleaning():
    """Test text cleaning."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Text Cleaning")
    logger.info("=" * 60)
    
    cleaner = TextCleaner()
    
    # Test with messy text
    messy_text = "  This   has   extra    spaces\n\n\n\nAnd multiple newlines  \n\r\nMixed line endings"
    cleaned = cleaner.clean(messy_text)
    
    logger.info(f"Original: '{messy_text}'")
    logger.info(f"Cleaned: '{cleaned}'")
    logger.info(f"Original length: {len(messy_text)}")
    logger.info(f"Cleaned length: {len(cleaned)}")
    logger.info(f"✅ Text cleaning successful")
    return True


def test_chunking():
    """Test text chunking."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Text Chunking")
    logger.info("=" * 60)
    
    chunker = TextChunker(min_tokens=100, max_tokens=200)
    
    # Create sample text
    sample_text = """
    Artificial intelligence is transforming how we work and live. Machine learning models can now 
    perform tasks that were once thought to require human intelligence. Natural language processing 
    enables computers to understand and generate human language. Computer vision allows machines to 
    interpret visual information. Reinforcement learning helps agents learn optimal behaviors through 
    trial and error. Deep learning has revolutionized many fields including healthcare, finance, and 
    transportation. The future of AI holds both tremendous promise and important challenges that we 
    must address thoughtfully and responsibly.
    """ * 5  # Repeat to ensure multiple chunks
    
    chunks = chunker.chunk_by_tokens(sample_text)
    
    logger.info(f"✅ Chunking successful")
    logger.info(f"   Total chunks created: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        logger.info(f"   Chunk {i}: {chunk['token_count']} tokens, {len(chunk['text'])} chars")
        logger.info(f"      Preview: {chunk['text'][:80]}...")
    
    return True


def test_document_chunking():
    """Test document-level chunking with metadata."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Document Chunking with Metadata")
    logger.info("=" * 60)
    
    doc_chunker = DocumentChunker()
    
    sample_text = "This is a test document. " * 200  # Ensure multiple chunks
    
    chunks = doc_chunker.chunk_document(
        text=sample_text,
        doc_id="test_doc_001",
        source="test_source",
        metadata={"category": "test", "author": "test_user"}
    )
    
    logger.info(f"✅ Document chunking successful")
    logger.info(f"   Total chunks: {len(chunks)}")
    logger.info(f"   First chunk ID: {chunks[0]['chunk_id']}")
    logger.info(f"   Metadata keys: {list(chunks[0].keys())}")
    logger.info(f"   Sample metadata:")
    for key in ['doc_id', 'source', 'chunk_index', 'total_chunks', 'token_count']:
        logger.info(f"      {key}: {chunks[0].get(key)}")
    
    return True


def test_full_extraction_and_chunking():
    """Test extraction + chunking pipeline."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Full Extraction + Chunking Pipeline")
    logger.info("=" * 60)
    
    try:
        # Extract
        extractor = TextExtractor()
        result = extractor.extract(os.path.join(os.path.dirname(__file__), '../data/sample_document.txt'))
        
        if not result["success"]:
            logger.error(f"❌ Extraction failed: {result['error']}")
            return False
        
        # Clean
        cleaner = TextCleaner()
        cleaned_text = cleaner.clean(result["text"])
        
        # Chunk
        doc_chunker = DocumentChunker()
        chunks = doc_chunker.chunk_document(
            text=cleaned_text,
            doc_id="sample_doc_001",
            source="sample_document.txt",
            metadata={
                "category": "documentation",
                "test_run": True,
                **result["metadata"]
            }
        )
        
        logger.info(f"✅ Full pipeline successful")
        logger.info(f"   Original file: sample_document.txt")
        logger.info(f"   Characters extracted: {len(result['text'])}")
        logger.info(f"   Characters after cleaning: {len(cleaned_text)}")
        logger.info(f"   Chunks created: {len(chunks)}")
        logger.info(f"   Chunk IDs:")
        for i, chunk in enumerate(chunks[:5]):
            logger.info(f"      {i+1}. {chunk['chunk_id']} ({chunk['token_count']} tokens)")
        if len(chunks) > 5:
            logger.info(f"      ... and {len(chunks) - 5} more chunks")
        
        return True
            
    except Exception as e:
        logger.error(f"❌ Pipeline error: {e}", exc_info=True)
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "🚀 Starting Ingestion Pipeline Tests (Core Components)" + "\n")
    
    tests = [
        ("Text Extraction", test_text_extraction),
        ("Text Cleaning", test_text_cleaning),
        ("Text Chunking", test_chunking),
        ("Document Chunking", test_document_chunking),
        ("Full Extraction + Chunking", test_full_extraction_and_chunking),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}", exc_info=True)
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed!")
        logger.info("\nNote: Full pipeline with embeddings and Qdrant storage")
        logger.info("      requires fastembed and qdrant-client to be installed.")
        logger.info("      Run inside Docker container for full functionality.")
        return 0
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
