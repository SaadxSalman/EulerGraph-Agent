from pathlib import Path

from .models import DocumentIngest

_SUPPORTED = {".md", ".markdown", ".txt", ".tex"}


def document_from_file(path: Path, author: str = "Imported document", kind: str = "reference") -> DocumentIngest:
    if path.suffix.lower() not in _SUPPORTED:
        raise ValueError(f"Unsupported file type: {path.suffix}. Use .md, .markdown, .txt, or .tex.")
    text = path.read_text(encoding="utf-8")
    if len(text.strip()) < 20:
        raise ValueError("The source file must contain at least 20 non-whitespace characters.")
    title = path.stem.replace("_", " ").replace("-", " ").strip().title()
    return DocumentIngest(title=title, author=author, kind=kind, text=text)


def split_sections(document: DocumentIngest, max_chars: int = 2400) -> list[DocumentIngest]:
    """Split long references on headings while retaining enough context per chunk."""
    sections: list[str] = []
    current: list[str] = []
    for line in document.text.splitlines():
        if line.lstrip().startswith("#") and current:
            sections.append("\n".join(current).strip())
            current = []
        current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    chunks: list[DocumentIngest] = []
    for index, section in enumerate(sections, start=1):
        for offset in range(0, len(section), max_chars):
            chunk = section[offset:offset + max_chars].strip()
            if len(chunk) >= 20:
                chunks.append(DocumentIngest(title=f"{document.title} · section {index}.{len(chunks) + 1}", author=document.author, kind=document.kind, text=chunk))
    return chunks
