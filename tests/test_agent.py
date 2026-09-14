import json

from fastapi.testclient import TestClient

from app.graph import EulerGraph
from app.ingest import document_from_file, split_sections
from app.main import app
from app.models import DocumentIngest, SolveRequest
from app.retrieval import HybridRetriever
from app.router import QueryRouter
from app.verifier import verify


def test_router_prioritizes_explicit_proof_mode():
    decision = QueryRouter().decide("Explain a matrix", "proof")
    assert decision.intent == "proof"
    assert decision.needs_formal_proof is True


def test_retrieval_ranks_matching_theorem(tmp_path):
    path = tmp_path / "documents.json"
    path.write_text(json.dumps([
        {"id": "a", "title": "Euler", "author": "E", "kind": "theorem", "text": "Euler formula exp(i x) equals cos x plus i sin x"},
        {"id": "b", "title": "Groups", "author": "G", "kind": "definition", "text": "A group has an identity element"},
    ]), encoding="utf-8")
    results = HybridRetriever(path).search("Euler formula")
    assert results[0].id == "a"
    assert results[0].relevance > 0


def test_duplicate_ingestion_gets_stable_suffix(tmp_path):
    retriever = HybridRetriever(tmp_path / "documents.json")
    document = DocumentIngest(title="Same theorem", text="A theorem with enough content for validation.")
    first = retriever.ingest(document)
    second = retriever.ingest(document)
    assert first.id == "same-theorem"
    assert second.id == "same-theorem-2"


def test_verifier_distinguishes_euler_identity():
    result = verify("Prove Euler identity", "exp(i*pi) + 1 = 0")
    assert result.status == "verified"
    assert result.checks


def test_file_ingestion_splits_sections(tmp_path):
    path = tmp_path / "analysis.md"
    path.write_text("# Limits\nA sufficiently long mathematical section for indexing.\n# Derivatives\nAnother sufficiently long section for indexing.", encoding="utf-8")
    document = document_from_file(path)
    chunks = split_sections(document, max_chars=100)
    assert len(chunks) == 2
    assert chunks[0].kind == "reference"


def test_api_contract():
    client = TestClient(app)
    response = client.post("/api/solve", json={"query": "Prove Euler identity from Euler formula", "mode": "proof"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["route"]["intent"] == "proof"
    assert payload["verification"]["status"] == "verified"
    assert len(payload["steps"]) == 4
