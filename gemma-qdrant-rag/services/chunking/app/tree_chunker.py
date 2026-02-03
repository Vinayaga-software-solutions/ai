from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .chunker import TextChunker


@dataclass
class TreeNode:
    node_type: str
    text: str = ""
    children: List["TreeNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent: Optional["TreeNode"] = None

    def add_child(self, child: "TreeNode") -> None:
        child.parent = self
        self.children.append(child)


class BaseDocumentParser:
    def parse(self, text: str) -> TreeNode:
        raise NotImplementedError


class UnsupportedDocumentParser(BaseDocumentParser):
    def __init__(self, doc_type: str, hint: str) -> None:
        self.doc_type = doc_type
        self.hint = hint

    def parse(self, text: str) -> TreeNode:
        raise UnsupportedDocumentTypeError(
            f"Document type '{self.doc_type}' requires an external parser. {self.hint}"
        )


class PlainTextParser(BaseDocumentParser):
    def parse(self, text: str) -> TreeNode:
        root = TreeNode("document")
        if text.strip():
            root.add_child(TreeNode("paragraph", text=text.strip()))
        return root


class MarkdownParser(BaseDocumentParser):
    def parse(self, text: str) -> TreeNode:
        root = TreeNode("document")
        stack: List[Tuple[int, TreeNode]] = [(0, root)]
        for line in text.splitlines():
            if not line.strip():
                continue
            heading_level = self._heading_level(line)
            if heading_level:
                heading_text = line.lstrip("#").strip()
                heading_node = TreeNode("section", text=heading_text, metadata={"level": heading_level})
                while stack and stack[-1][0] >= heading_level:
                    stack.pop()
                stack[-1][1].add_child(heading_node)
                stack.append((heading_level, heading_node))
            else:
                paragraph_node = TreeNode(
                    "paragraph",
                    text=line.strip(),
                    metadata=self._extract_inline_metadata(line),
                )
                stack[-1][1].add_child(paragraph_node)
        return root

    def _heading_level(self, line: str) -> Optional[int]:
        if line.startswith("#"):
            return len(line) - len(line.lstrip("#"))
        return None

    def _extract_inline_metadata(self, text: str) -> Dict[str, Any]:
        return {
            "bold_terms": self._extract_terms(text, r"\*\*(.+?)\*\*"),
            "italic_terms": self._extract_terms(text, r"\*(.+?)\*"),
            "links": self._extract_links(text),
        }

    def _extract_terms(self, text: str, pattern: str) -> List[str]:
        return [match.strip() for match in re_findall(pattern, text)]

    def _extract_links(self, text: str) -> List[Dict[str, str]]:
        links = []
        for label, href in re_findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
            links.append({"text": label.strip(), "href": href.strip()})
        return links


class SimpleHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root = TreeNode("document")
        self.stack: List[Tuple[int, TreeNode]] = [(0, self.root)]
        self.current_text: List[str] = []
        self.current_heading: Optional[TreeNode] = None
        self.inline_metadata: Dict[str, Any] = {"bold_terms": [], "italic_terms": [], "links": []}
        self.current_link: Optional[Dict[str, str]] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._flush_paragraph()
            level = int(tag[1])
            heading_node = TreeNode("section", metadata={"level": level})
            while self.stack and self.stack[-1][0] >= level:
                self.stack.pop()
            self.stack[-1][1].add_child(heading_node)
            self.stack.append((level, heading_node))
            self.current_heading = heading_node
        elif tag in {"strong", "b"}:
            self.current_text.append("**")
        elif tag in {"em", "i"}:
            self.current_text.append("*")
        elif tag == "a":
            href = dict(attrs).get("href") or ""
            self.current_link = {"text": "", "href": href}

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if self.current_heading:
                self.current_heading.text = "".join(self.current_text).strip()
            self.current_heading = None
            self.current_text = []
        elif tag in {"p", "li"}:
            self._flush_paragraph()
        elif tag in {"strong", "b"}:
            self.current_text.append("**")
        elif tag in {"em", "i"}:
            self.current_text.append("*")
        elif tag == "a":
            if self.current_link:
                self.inline_metadata["links"].append(self.current_link)
            self.current_link = None

    def handle_data(self, data: str) -> None:
        if self.current_link is not None:
            self.current_link["text"] += data
        self.current_text.append(data)

    def _flush_paragraph(self) -> None:
        text = "".join(self.current_text).strip()
        if text:
            paragraph_node = TreeNode(
                "paragraph",
                text=text,
                metadata={
                    "bold_terms": self._extract_terms(text, r"\*\*(.+?)\*\*"),
                    "italic_terms": self._extract_terms(text, r"\*(.+?)\*"),
                    "links": list(self.inline_metadata["links"]),
                },
            )
            self.stack[-1][1].add_child(paragraph_node)
        self.current_text = []
        self.inline_metadata = {"bold_terms": [], "italic_terms": [], "links": []}

    def _extract_terms(self, text: str, pattern: str) -> List[str]:
        return [match.strip() for match in re_findall(pattern, text)]


class HTMLDocumentParser(BaseDocumentParser):
    def parse(self, text: str) -> TreeNode:
        parser = SimpleHTMLParser()
        parser.feed(text)
        parser._flush_paragraph()
        return parser.root


class UnsupportedDocumentTypeError(ValueError):
    pass


class DocumentParserRegistry:
    def __init__(self, parsers: Optional[Dict[str, BaseDocumentParser]] = None) -> None:
        self.parsers = parsers or {
            "plain": PlainTextParser(),
            "markdown": MarkdownParser(),
            "md": MarkdownParser(),
            "html": HTMLDocumentParser(),
            "htm": HTMLDocumentParser(),
            "pdf": UnsupportedDocumentParser("pdf", "Use a PDF extractor like pdfplumber and pass text."),
            "doc": UnsupportedDocumentParser("doc", "Convert to text or DOCX before chunking."),
            "docx": UnsupportedDocumentParser("docx", "Use python-docx and pass text."),
            "word": UnsupportedDocumentParser("word", "Convert to text or DOCX before chunking."),
        }

    def get_parser(self, doc_type: str) -> BaseDocumentParser:
        parser = self.parsers.get(doc_type.lower())
        if not parser:
            raise UnsupportedDocumentTypeError(
                f"Unsupported document type '{doc_type}'. "
                "Configure a parser for it or convert to markdown/plain text."
            )
        return parser

    def register(self, doc_type: str, parser: BaseDocumentParser) -> None:
        self.parsers[doc_type.lower()] = parser


class SemanticInterpreter:
    def __init__(self, mapping: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self.mapping = mapping or {
            "bold": {"signal": "importance_high", "weight": 1.0},
            "italic": {"signal": "importance_medium", "weight": 0.5},
            "link": {"signal": "reference", "weight": 0.8},
            "heading": {"signal": "section_boundary", "weight": 1.0},
        }

    def interpret(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "semantic_signals": {
                "bold": self.mapping.get("bold", {}),
                "italic": self.mapping.get("italic", {}),
                "link": self.mapping.get("link", {}),
                "heading": self.mapping.get("heading", {}),
            },
            "formatting": {
                "bold_terms": metadata.get("bold_terms", []),
                "italic_terms": metadata.get("italic_terms", []),
                "links": metadata.get("links", []),
            },
        }


class TreeChunker:
    def __init__(
        self,
        token_chunker: Optional[TextChunker] = None,
        parser_registry: Optional[DocumentParserRegistry] = None,
        interpreter: Optional[SemanticInterpreter] = None,
    ) -> None:
        self.token_chunker = token_chunker or TextChunker()
        self.parser_registry = parser_registry or DocumentParserRegistry()
        self.interpreter = interpreter or SemanticInterpreter()

    def chunk_document(
        self,
        text: str,
        doc_id: str,
        source: str,
        doc_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        semantic_mapping: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        parser = self.parser_registry.get_parser(doc_type)
        root = parser.parse(text)

        interpreter = self.interpreter
        if semantic_mapping is not None:
            interpreter = SemanticInterpreter(semantic_mapping)

        base_metadata = {
            "doc_id": doc_id,
            "source": source,
            "doc_type": doc_type,
            **(metadata or {}),
        }

        subtree_chunks = []
        subtree_nodes = self._collect_subtree_roots(root)
        if not subtree_nodes:
            subtree_nodes = [root]

        for subtree in subtree_nodes:
            subtree_text = self._flatten_text(subtree)
            subtree_metadata = self._collect_metadata(subtree)
            semantic_metadata = interpreter.interpret(subtree_metadata)
            chunk_metadata = {
                **base_metadata,
                **semantic_metadata,
                "heading_path": self._heading_path(subtree),
            }
            subtree_chunks.extend(self.token_chunker.chunk_by_tokens(subtree_text, chunk_metadata))

        for i, chunk in enumerate(subtree_chunks):
            chunk["chunk_id"] = f"{doc_id}_chunk_{i}"
            chunk["total_chunks"] = len(subtree_chunks)

        return subtree_chunks

    def _collect_subtree_roots(self, root: TreeNode) -> List[TreeNode]:
        return [
            node
            for node in self._walk(root)
            if node.node_type == "section" and (node.parent is None or node.parent.node_type != "section")
        ]

    def _walk(self, node: TreeNode) -> Iterable[TreeNode]:
        yield node
        for child in node.children:
            yield from self._walk(child)

    def _flatten_text(self, node: TreeNode) -> str:
        parts = []
        if node.text:
            parts.append(node.text)
        for child in node.children:
            parts.append(self._flatten_text(child))
        return "\n".join(part for part in parts if part)

    def _collect_metadata(self, node: TreeNode) -> Dict[str, Any]:
        metadata = {"bold_terms": [], "italic_terms": [], "links": []}
        if node.metadata:
            metadata["bold_terms"].extend(node.metadata.get("bold_terms", []))
            metadata["italic_terms"].extend(node.metadata.get("italic_terms", []))
            metadata["links"].extend(node.metadata.get("links", []))
        for child in node.children:
            child_meta = self._collect_metadata(child)
            metadata["bold_terms"].extend(child_meta.get("bold_terms", []))
            metadata["italic_terms"].extend(child_meta.get("italic_terms", []))
            metadata["links"].extend(child_meta.get("links", []))
        return metadata

    def _heading_path(self, node: TreeNode) -> List[str]:
        if node.node_type != "section":
            return []
        path = []
        current: Optional[TreeNode] = node
        while current is not None:
            if current.node_type == "section" and current.text:
                path.insert(0, current.text)
            current = current.parent
        return path


def re_findall(pattern: str, text: str) -> List[Any]:
    import re

    return re.findall(pattern, text)
