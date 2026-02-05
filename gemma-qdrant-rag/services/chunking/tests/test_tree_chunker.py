from app.tree_chunker import TreeChunker


def test_tree_chunker_markdown_semantics():
    chunker = TreeChunker()
    text = "# Title\nThis is **bold** text with a [link](https://example.com)."

    chunks = chunker.chunk_document(
        text=text,
        doc_id="doc1",
        source="unit-test",
        doc_type="markdown",
        semantic_mapping={
            "bold": {"signal": "key_term", "weight": 2.0},
            "italic": {"signal": "secondary", "weight": 0.5},
            "link": {"signal": "citation", "weight": 1.0},
            "heading": {"signal": "section", "weight": 1.0},
        },
    )

    assert chunks
    assert chunks[0]["doc_type"] == "markdown"
    assert "Title" in chunks[0]["heading_path"]
    assert chunks[0]["formatting"]["bold_terms"] == ["bold"]
    assert chunks[0]["formatting"]["links"][0]["href"] == "https://example.com"
    assert chunks[0]["semantic_signals"]["bold"]["signal"] == "key_term"
    assert chunks[0]["parent_section"] is None
    assert chunks[0]["section_hierarchy"][0]["title"] == "Title"
