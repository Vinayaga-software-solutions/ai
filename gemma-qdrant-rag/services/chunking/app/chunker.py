from typing import List, Dict, Any
import tiktoken
import re


class TextChunker:
    def __init__(
        self,
        min_tokens: int = 100,
        max_tokens: int = 500,
        overlap_tokens: int = 50,
        encoding_name: str = "cl100k_base",
    ):
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def chunk_by_tokens(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        sentences = self._split_into_sentences(text)

        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            if current_tokens + sentence_tokens > self.max_tokens:
                if current_tokens >= self.min_tokens:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
                    current_chunk = self._get_overlap_sentences(current_chunk)
                    current_tokens = self.count_tokens(" ".join(current_chunk))

                if sentence_tokens > self.max_tokens:
                    sub_chunks = self._split_long_sentence(sentence)
                    for sub_chunk in sub_chunks:
                        chunks.append(self._create_chunk(sub_chunk, len(chunks), metadata))
                    current_chunk = []
                    current_tokens = 0
                else:
                    current_chunk.append(sentence)
                    current_tokens += sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        if current_chunk and current_tokens >= self.min_tokens:
            chunk_text = " ".join(current_chunk)
            chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
        elif current_chunk and chunks:
            last_chunk_text = " ".join(current_chunk)
            chunks[-1]["text"] += " " + last_chunk_text

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_long_sentence(self, sentence: str) -> List[str]:
        words = sentence.split()
        chunks = []
        current_chunk = []
        current_tokens = 0

        for word in words:
            word_tokens = self.count_tokens(word)
            if current_tokens + word_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_tokens = word_tokens
            else:
                current_chunk.append(word)
                current_tokens += word_tokens

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        overlap_text = ""
        overlap_sentences = []

        for sentence in reversed(sentences):
            test_text = sentence + " " + overlap_text
            if self.count_tokens(test_text) <= self.overlap_tokens:
                overlap_sentences.insert(0, sentence)
                overlap_text = test_text
            else:
                break

        return overlap_sentences

    def _create_chunk(self, text: str, chunk_index: int, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        chunk = {
            "text": text,
            "chunk_index": chunk_index,
            "token_count": self.count_tokens(text),
        }

        if metadata:
            chunk.update(metadata)

        return chunk


class DocumentChunker:
    def __init__(self, token_chunker: TextChunker = None):
        self.token_chunker = token_chunker or TextChunker()

    def chunk_document(self, text: str, doc_id: str, source: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        base_metadata = {
            "doc_id": doc_id,
            "source": source,
            **(metadata or {}),
        }

        chunks = self.token_chunker.chunk_by_tokens(text, base_metadata)

        for i, chunk in enumerate(chunks):
            chunk["chunk_id"] = f"{doc_id}_chunk_{i}"
            chunk["total_chunks"] = len(chunks)

        return chunks
