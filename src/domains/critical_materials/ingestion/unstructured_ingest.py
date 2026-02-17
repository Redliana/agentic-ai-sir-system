"""Unstructured ingestion helpers for reports and policy documents."""

import os
from typing import Any, Dict, List, Optional


SUPPORTED_UNSTRUCTURED_EXTENSIONS = {".txt", ".md", ".pdf"}


class MissingDependencyError(RuntimeError):
    """Raised when an optional parser dependency is not installed."""


def _split_text(text: str, chunk_size: int, chunk_overlap: int = 0) -> List[str]:
    words = text.split()
    if not words:
        return []

    size = max(1, chunk_size)
    overlap = max(0, min(chunk_overlap, size - 1))
    step = max(1, size - overlap)

    chunks = []
    for idx in range(0, len(words), step):
        chunk_words = words[idx : idx + size]
        if not chunk_words:
            continue
        chunks.append(" ".join(chunk_words))
        if idx + size >= len(words):
            break
    return chunks


def _read_text_file(path: str) -> str:
    with open(path, "r") as file:
        return file.read().strip()


def _read_pdf_pages(path: str) -> List[Dict[str, Any]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise MissingDependencyError(
            "pypdf is required for .pdf ingestion. Install with: python3 -m pip install pypdf"
        ) from exc

    reader = PdfReader(path)
    pages = []
    for page_idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        pages.append({"page_number": page_idx, "text": text})
    return pages


def _build_document_chunks(
    *,
    source_path: str,
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    page_number: Optional[int],
) -> List[Dict[str, Any]]:
    docs = []
    source_name = os.path.basename(source_path)
    for idx, chunk in enumerate(_split_text(text, chunk_size, chunk_overlap)):
        doc_id = f"{source_name}:{idx}"
        if page_number is not None:
            doc_id = f"{source_name}:page{page_number}:{idx}"
        docs.append(
            {
                "doc_id": doc_id,
                "source_path": source_path,
                "page_number": page_number,
                "text_content": chunk,
            }
        )
    return docs


def ingest_unstructured_sources(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load plain-text and PDF sources and return chunked documents."""
    config = config or {}
    source_paths = config.get("source_paths", [])
    chunk_size = int(config.get("chunk_size", 180))
    chunk_overlap = int(config.get("chunk_overlap", 0))

    documents: List[Dict[str, Any]] = []
    missing_paths: List[str] = []
    unsupported_paths: List[str] = []
    failed_paths: List[Dict[str, str]] = []
    missing_dependencies: List[str] = []

    for path in source_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
            continue

        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_UNSTRUCTURED_EXTENSIONS:
            unsupported_paths.append(path)
            continue

        try:
            if ext in {".txt", ".md"}:
                text = _read_text_file(path)
                documents.extend(
                    _build_document_chunks(
                        source_path=path,
                        text=text,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        page_number=None,
                    )
                )
            else:
                for page in _read_pdf_pages(path):
                    documents.extend(
                        _build_document_chunks(
                            source_path=path,
                            text=page["text"],
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap,
                            page_number=page["page_number"],
                        )
                    )
        except MissingDependencyError as exc:
            message = str(exc)
            if message not in missing_dependencies:
                missing_dependencies.append(message)
            failed_paths.append({"path": path, "error": message})
            continue
        except Exception as exc:  # pragma: no cover - protection for malformed files
            failed_paths.append({"path": path, "error": str(exc)})
            continue

    status = "ok" if not missing_paths and not unsupported_paths and not failed_paths else "partial"
    return {
        "status": status,
        "documents": documents,
        "document_count": len(documents),
        "missing_paths": missing_paths,
        "unsupported_paths": unsupported_paths,
        "failed_paths": failed_paths,
        "missing_dependencies": missing_dependencies,
    }
