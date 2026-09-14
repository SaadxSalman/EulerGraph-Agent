from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .graph import EulerGraph
from .models import CorpusStats, DocumentIngest, HealthResponse, SolveRequest, SolveResponse
from .observability import configure_logging

configure_logging()
settings = get_settings()
engine = EulerGraph(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="web"), name="static")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("web/index.html")


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="operational", retrieval="local hybrid index", llm="configured" if engine.provider.remote else "local fallback", documents=len(engine.retriever.documents))


@app.post("/api/solve", response_model=SolveResponse)
async def solve(request: SolveRequest):
    return await engine.solve(request)


@app.post("/api/documents", response_model=dict)
async def ingest(document: DocumentIngest):
    source = engine.retriever.ingest(document)
    return {"document": source, "message": "Document indexed successfully"}


@app.get("/api/corpus", response_model=CorpusStats)
async def corpus_stats():
    return engine.retriever.stats()
