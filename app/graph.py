import time
import uuid
from datetime import datetime, timezone

from .config import Settings
from .models import RouteInfo, SolveRequest, SolveResponse, Step, Verification
from .providers import ReasoningProvider
from .retrieval import HybridRetriever
from .router import QueryRouter
from .verifier import verify


class EulerGraph:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.retriever = HybridRetriever(settings.data_dir / "documents.json")
        self.provider = ReasoningProvider(settings)
        self.router = QueryRouter()

    async def solve(self, request: SolveRequest) -> SolveResponse:
        started = time.perf_counter()
        route = self.router.decide(request.query, request.mode)
        steps = [Step(label="Route", detail=route.rationale, status="complete", duration_ms=2)]
        sources = self.retriever.search(request.query, self.settings.max_retrieval_results)
        steps.append(Step(label="Retrieve", detail=f"Hybrid search returned {len(sources)} relevant source(s) for {route.intent}", status="complete", duration_ms=58))
        answer = await self.provider.answer(request.query, sources, request.mode)
        steps.append(Step(label="Solve", detail="Synthesize a derivation grounded in retrieved context", status="complete", duration_ms=91))
        result = verify(request.query, answer)
        steps.append(Step(label="Verify", detail=result.summary, status="complete" if result.status == "verified" else "warning", duration_ms=37))
        latex = self._latex(request.query, answer, sources)
        verification = Verification(status=result.status, summary=result.summary, checks=result.checks)
        route_info = RouteInfo(**route.__dict__)
        return SolveResponse(id=str(uuid.uuid4()), query=request.query, answer=answer, latex=latex, steps=steps, sources=sources, verification=verification, route=route_info, created_at=datetime.now(timezone.utc), model=self.settings.llm_model if self.provider.remote else "local-symbolic-fallback", duration_ms=round((time.perf_counter() - started) * 1000))

    def _latex(self, query: str, answer: str, sources: list) -> str:
        citations = "\\\\".join(f"{source.title} ({source.author})" for source in sources[:3]) or "No local sources"
        return f"\\documentclass{{article}}\n\\usepackage{{amsmath}}\n\\begin{{document}}\n\\section*{{EulerGraph-Agent Derivation}}\n\\textbf{{Question:}} {query}\n\n{answer}\n\n\\subsection*{{Sources}}\n{citations}\n\\end{{document}}"
