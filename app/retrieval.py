import json
import math
import re
from pathlib import Path
from threading import RLock

from .models import CorpusStats, DocumentIngest, Source

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


class HybridRetriever:
    def __init__(self, path: Path):
        self.path = path
        self._lock = RLock()
        self.documents: list[dict] = []
        self._load()

    def _load(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self.documents = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.documents = []

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.documents, indent=2), encoding="utf-8")

    def search(self, query: str, limit: int = 6) -> list[Source]:
        query_terms = set(_TOKEN_RE.findall(query.lower()))
        scored = []
        for document in self.documents:
            haystack = f"{document['title']} {document['kind']} {document['text']}".lower()
            terms = _TOKEN_RE.findall(haystack)
            lexical = sum(1 for term in query_terms if term in terms) / max(len(query_terms), 1)
            phrase_bonus = 0.15 if query.lower() in haystack else 0
            semantic_proxy = sum(math.log1p(terms.count(term)) for term in query_terms) / max(math.log1p(len(terms)), 1)
            score = min(1.0, lexical * 0.65 + semantic_proxy * 0.25 + phrase_bonus)
            if score > 0:
                scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [self._source(document, score) for score, document in scored[:limit]]

    def ingest(self, document: DocumentIngest) -> Source:
        with self._lock:
            item = document.model_dump()
            item["id"] = re.sub(r"[^a-z0-9]+", "-", document.title.lower()).strip("-") or "document"
            suffix = 2
            existing = {entry["id"] for entry in self.documents}
            base_id = item["id"]
            while item["id"] in existing:
                item["id"] = f"{base_id}-{suffix}"
                suffix += 1
            self.documents.append(item)
            self._save()
            return self._source(item, 1.0)

    def stats(self) -> CorpusStats:
        kinds: dict[str, int] = {}
        for document in self.documents:
            kind = document.get("kind", "unknown")
            kinds[kind] = kinds.get(kind, 0) + 1
        average_length = round(sum(len(document.get("text", "")) for document in self.documents) / max(len(self.documents), 1))
        return CorpusStats(documents=len(self.documents), kinds=kinds, authors=len({document.get("author", "Unknown") for document in self.documents}), average_length=average_length)

    def _source(self, document: dict, score: float) -> Source:
        return Source(id=document["id"], title=document["title"], author=document["author"], kind=document["kind"], excerpt=document["text"], relevance=round(score, 3))
