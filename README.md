# EulerGraph-Agent

EulerGraph-Agent is a local-first, full-stack Retrieval-Augmented Generation (RAG) workspace for turning difficult mathematical questions into traceable, verifiable derivations. It is designed around a simple principle: a useful mathematical answer should expose its path, its evidence, and the limits of its verification.

The project combines a FastAPI service, a browser-based reasoning workspace, a persistent lightweight hybrid retriever, provider-aware response generation, and a symbolic verification boundary. It runs with no paid API key and no external database. Optional remote LLM and vector database credentials can be added later through the single ignored `.env` file.

## What it does

Given a question such as “Prove Euler's identity from Euler's formula”, the graph executes four visible stages:

1. **Route** classifies the mathematical intent and chooses the available tools.
2. **Retrieve** searches theorem blocks and definitions using lexical overlap plus a lightweight semantic proxy. This local fallback is deterministic and useful during development.
3. **Solve** synthesizes a derivation grounded in the retrieved evidence. A remote provider can be introduced behind the same provider boundary without changing the API or UI contract.
4. **Verify** applies a symbolic or claim-specific check. The service reports `verified`, `partial`, or `unverified`; it does not silently promote an unproven answer to a proof.

Every response includes the query, answer, LaTeX export, ordered trace steps, source evidence, verification checks, model mode, timestamp, and duration.

## Product surface

The home screen is the working interface rather than a marketing page. It includes:

- A large mathematical query editor.
- Four reasoning modes: Auto, Proof, Compute, and Explain.
- Keyboard execution with Ctrl+Enter on Windows and Linux or Cmd+Enter on macOS.
- A live-style Route → Retrieve → Solve → Verify trace.
- A derivation panel with the verification badge.
- Source cards showing title, kind, relevance, author, and excerpt.
- One-click LaTeX copying.
- Downloadable `.tex` export.
- A health indicator showing the index size and whether a remote LLM is configured.
- Automatic responsive behavior for narrow screens.

## Architecture

```text
Browser
  |
  | GET /, POST /api/solve, GET /api/health
  v
FastAPI application (app/main.py)
  |
  v
EulerGraph orchestration (app/graph.py)
  |             |                 |
  v             v                 v
Retriever     Provider          Verifier
JSON index    local fallback    SymPy boundary
or future     or future API     + claim checks
Qdrant
```

### Backend modules

- `app/main.py` owns HTTP routes, CORS, static files, and application lifecycle.
- `app/config.py` owns settings and `.env` loading. Settings are cached so the graph shares one configuration object.
- `app/models.py` defines the public Pydantic contract. These models are deliberately explicit so clients can render trace and evidence without inspecting internal objects.
- `app/graph.py` is the orchestration boundary. It keeps the route order and response assembly in one place.
- `app/retrieval.py` owns the document index, hybrid scoring, persistence, and ingestion. The current implementation is intentionally dependency-light and offline-friendly.
- `app/providers.py` owns reasoning generation. The local provider gives a helpful deterministic experience while keys are absent; the `remote` flag is ready for a production adapter.
- `app/verifier.py` is the verification boundary. It uses SymPy only for controlled symbolic checks and distinguishes partial proof-shaped responses from verified identities.
- `data/documents.json` is the starter corpus. It contains theorem and definition blocks that make the first run useful immediately.
- `web/index.html`, `web/styles.css`, and `web/app.js` are a zero-build frontend served by FastAPI. This keeps setup fast and makes the deployed artifact easy to understand.

## Requirements

- Python 3.11 or newer. Python 3.14 is supported by the current environment.
- A modern browser.
- Git, if you want to version the project.
- Optional: an OpenAI or Anthropic API key for a remote reasoning adapter.
- Optional: Qdrant credentials when replacing the local index with a hosted vector store.

No Node.js installation is required for the included frontend.

## Installation

Open PowerShell in the project root:

```powershell
cd "S:\My Data\Github\EulerGraph-Agent"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run the project interpreter directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The repository intentionally contains one real `.env` file and no `.env.example`. It is ignored by `.gitignore`. Fill in values locally as needed:

```dotenv
APP_NAME=EulerGraph-Agent
ENVIRONMENT=development
API_HOST=127.0.0.1
API_PORT=8000
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=claude-3-5-sonnet-latest
DATA_DIR=data
MAX_RETRIEVAL_RESULTS=6
```

Do not put credentials in Python, JavaScript, README files, commit messages, or browser code. The frontend only talks to the backend; provider keys never leave the server process.

## Run locally

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser. The interactive API schema is available at `/docs` and the OpenAPI JSON document is at `/openapi.json`.

The first page load should show five indexed sources and `local fallback`. Run the pre-filled Euler identity query to see a verified trace.

## API reference

### `GET /api/health`

Returns a compact operational view:

```json
{
  "status": "operational",
  "retrieval": "local hybrid index",
  "llm": "local fallback",
  "documents": 5
}
```

`llm` becomes `configured` when either supported provider key is present. This flag describes configuration only; production adapters should still report provider failures explicitly.

### `POST /api/solve`

Request:

```json
{
  "query": "Prove Euler identity from Euler formula",
  "mode": "proof",
  "source_ids": []
}
```

`mode` accepts `auto`, `proof`, `compute`, or `explain`. `source_ids` is reserved for a future pinned-evidence workflow and is accepted in the contract today.

The response has these important fields:

- `answer`: readable derivation text.
- `latex`: publication-oriented LaTeX document string.
- `steps`: ordered orchestration trace with status and duration.
- `sources`: retrieved evidence with relevance scores.
- `verification`: status, summary, and checks.
- `model`: configured remote model name or `local-symbolic-fallback`.
- `duration_ms`: end-to-end graph duration.

PowerShell example:

```powershell
$body = @{ query = "Prove Euler identity from Euler formula"; mode = "proof" } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/solve -Method Post -ContentType "application/json" -Body $body
```

### `POST /api/documents`

Adds a theorem, paper excerpt, textbook passage, or personal note to the persistent local index.

```json
{
  "title": "A useful lemma",
  "author": "Research notes",
  "kind": "lemma",
  "text": "A sufficiently long theorem or definition block goes here..."
}
```

The generated document id is a normalized title, with a numeric suffix when a title already exists. The index is written back to `data/documents.json` immediately.

## Retrieval details

The starter retriever is deliberately transparent. It tokenizes the query and each document, computes keyword coverage, adds a frequency-based semantic proxy, and awards a small exact phrase bonus. Scores are bounded to `[0, 1]` and sorted descending. This is not presented as a replacement for learned embeddings; it is a reliable local baseline that makes behavior observable and tests reproducible.

A production implementation can replace `HybridRetriever.search` with a Qdrant adapter that stores:

- Dense vectors from `EMBEDDING_MODEL`.
- Sparse BM25 or SPLADE-style token weights.
- Chunk metadata such as paper id, page, section, equation label, and source URL.
- LaTeX-preserving text alongside normalized text.

The public `Source` model should remain stable while the backing store evolves.

## Verification strategy

Verification is intentionally conservative:

- Known Euler identity responses are checked against the canonical relation `exp(i*pi) + 1 = 0`.
- Calculus-shaped questions execute a controlled SymPy identity check and report the result in `checks`.
- Proof requests without a formal theorem prover receive `partial` rather than `verified`.
- General grounded answers report that no contradiction was detected, which is weaker than a proof.

For higher assurance, add a sandboxed execution service and a Lean 4 adapter. Never execute arbitrary model-produced Python in the API process. A safe extension should parse an allow-listed expression language, run in a resource-limited worker, capture stdout and diagnostics, and return structured evidence to the verifier.

## Remote provider roadmap

The provider boundary in `app/providers.py` is intentionally small:

```python
async def answer(query: str, sources: list[Source], mode: str) -> str:
    ...
```

A production adapter should:

1. Keep all credentials server-side.
2. Set request and token timeouts.
3. Retry only idempotent, transient failures with bounded backoff.
4. Preserve the retrieved source ids in the prompt and response metadata.
5. Refuse unsupported claims rather than inventing citations.
6. Log latency and provider request ids without logging secrets or full private documents.
7. Add rate limiting and authentication before exposing the service publicly.

The configured model names in `.env` are defaults, not a claim that a remote integration is active.

## Security and privacy

- `.env` is ignored by Git and is the only location intended for local keys.
- `.env.example` is intentionally not included.
- CORS is permissive for local development. Restrict `allow_origins` before deployment.
- The document index may contain private research notes. Treat `data/documents.json` as sensitive if you ingest proprietary material.
- The current ingestion endpoint has no authentication. Put it behind an authenticated gateway before sharing it.
- Do not expose the development server directly to the public internet.
- Add request size limits, authentication, structured audit logs, and per-user document namespaces for a multi-user deployment.

Verify secret protection before the first push:

```powershell
git check-ignore .env
 git status --short
```

The first command should print `.env`, and `.env` should not appear in the status output.

## Testing and quality checks

Compile all Python modules:

```powershell
.\.venv\Scripts\python.exe -m compileall app
```

Run a direct API smoke test:

```powershell
.\.venv\Scripts\python.exe -c "from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); print(c.get('/api/health').json()); print(c.post('/api/solve', json={'query':'Prove Euler identity from Euler formula','mode':'proof'}).json()['verification'])"
```

For a production codebase, add pytest coverage for retrieval ranking, duplicate ingestion ids, validation errors, provider fallback, every verification status, and the LaTeX export contract. Add browser tests for query execution, mode selection, copy/download actions, and narrow viewport rendering.

## Extending the system

### Add a source document

Use the API or edit `data/documents.json` while the server is stopped. API ingestion is safer because it validates shape and generates ids.

### Add a new mathematical verifier

Keep the verifier pure and return a structured result. Add a narrow trigger, a bounded symbolic operation, and an explicit failure path. A verifier must never catch every exception and label the result verified.

### Add a real vector database

Create an adapter implementing `search` and `ingest`, map its records into `Source`, and select it from settings. Keep the local retriever available for development and offline operation.

### Add LangGraph

The current `EulerGraph.solve` method is intentionally shaped as a stateful orchestration boundary. It can be migrated to LangGraph nodes with a typed state containing query, mode, sub-tasks, retrieved sources, draft, critiques, and verification attempts. Preserve the response model so the current frontend remains compatible.

### Add Lean 4

Compile generated propositions in a separate Lean worker or service. Return theorem names, compiler diagnostics, and the exact checked proposition as structured verification evidence. Keep uncompiled prose separate from formally checked proof terms.

## Design principles

- Local-first: the product should remain useful before cloud setup.
- Evidence before confidence: retrieved sources and checks are visible.
- Honest status: partial verification is a first-class result.
- Stable contracts: UI, API, retriever, provider, and verifier evolve behind typed boundaries.
- Small dependencies: every dependency should earn its operational cost.
- Reproducible behavior: deterministic local retrieval and fallback answers make development pleasant.

## License

No license has been added yet. Choose and add one before distributing the project.

## Project map

The repository is intentionally organized around stable responsibilities:

```text
EulerGraph-Agent/
├── app/
│   ├── __init__.py          package marker
│   ├── cli.py               ask, ingest, and stats command line interface
│   ├── config.py            typed environment settings
│   ├── graph.py             Route -> Retrieve -> Solve -> Verify orchestration
│   ├── ingest.py             file validation and section-aware chunking
│   ├── main.py              FastAPI application and HTTP endpoints
│   ├── models.py            request, response, and domain schemas
│   ├── observability.py     JSON logs and timing context manager
│   ├── providers.py         local fallback and future remote model boundary
│   ├── retrieval.py         persistent local hybrid index
│   ├── router.py            deterministic intent and tool routing
│   └── verifier.py          conservative symbolic and claim checks
├── data/
│   └── documents.json       starter theorem and definition corpus
├── docs/
│   ├── architecture.md     lifecycle, boundaries, state, and scaling
│   ├── contributing.md     development and review conventions
│   └── deployment.md       Docker, operations, secrets, and security
├── tests/
│   └── test_agent.py        routing, retrieval, ingestion, verification, API
├── web/
│   ├── app.js               query execution and result rendering
│   ├── index.html           working interface shell
│   └── styles.css           responsive visual system
├── .env                    local secrets and settings; ignored by Git
├── Dockerfile               production-shaped container entrypoint
├── pyproject.toml           package metadata and tool configuration
└── requirements.txt         runtime and test dependencies
```

## CLI cookbook

The CLI is useful when a browser is not available, when importing a folder is part of a batch job, or when a result needs to be captured in automation.

### Ask a question

```powershell
.\.venv\Scripts\python.exe -m app.cli ask "Explain the rank nullity theorem" --mode explain
```

The command emits the same response shape used by the HTTP API. It is JSON so it can be redirected to an artifact, inspected with PowerShell, or processed by another program.

### Inspect the corpus

```powershell
.\.venv\Scripts\python.exe -m app.cli stats
```

This reports document count, distinct authors, document kinds, and average text length. These metrics are small but useful early warnings for an empty or accidentally polluted corpus.

### Import a reference

```powershell
.\.venv\Scripts\python.exe -m app.cli ingest .\notes\real-analysis.md --author "Research notes" --kind "notes"
```

Supported suffixes are `.md`, `.markdown`, `.txt`, and `.tex`. Markdown headings create section boundaries. Long sections are split into bounded chunks; each chunk receives a title containing its source section and chunk ordinal. The default chunk size is 2,400 characters and can be changed with `--chunk-size`.

## Query behavior matrix

| Input signal | Route intent | Retrieval | Symbolic check | Formal proof flag |
| --- | --- | --- | --- | --- |
| `proof`, `prove`, `derive` | proof | yes | yes | yes |
| `derivative`, `integral`, `limit` | calculus | yes | yes | no |
| `matrix`, `eigenvalue`, `group` | algebra | yes | depends on mode | no |
| `calculate`, `evaluate`, `simplify` | computation | yes | yes | no |
| no recognized signal | explanation | yes | no | no |

An explicit mode is authoritative for proof routing. This is important for a user who asks “Explain a matrix” but selects Proof: the graph should reveal that the requested rigor level changes the route.

## Response interpretation

`verified` means a specific local check passed. It does not mean every sentence in the answer has been formally proven. `partial` means the answer is grounded or plausible but the available verifier did not establish the entire claim. `unverified` is reserved for a future provider or verifier path that explicitly cannot make a determination.

Source relevance is a ranking signal, not a confidence score. A highly relevant source can still be incomplete or misapplied. The UI keeps the evidence visible so a mathematician can inspect the excerpt and decide whether the hypotheses match the problem.

## Mathematical correctness policy

The system should preserve the difference between:

- A definition copied from a source.
- A theorem applied under its hypotheses.
- An algebraic transformation.
- A numerical or symbolic computation.
- A formal proof checked by a theorem prover.

When extending the provider, prompt and parse for these distinctions. When extending the verifier, record each check separately. Do not collapse them into one confidence percentage: a probability-like score can suggest precision that the underlying evidence does not support.

## Source provenance recommendations

For scholarly ingestion, extend `DocumentIngest` with optional fields such as `source_url`, `publication`, `year`, `page`, `section`, `equation_label`, and `content_hash`. Preserve original LaTeX alongside normalized plain text. A chunk should be able to answer “where did this statement come from?” without relying on a model-generated citation.

For arXiv or publisher workflows, store metadata separately from content and keep licensing information explicit. Do not bundle copyrighted books or papers into this repository without permission. The included corpus consists of short, generic reference statements intended as starter data.

## Production hardening sequence

The recommended order for taking this prototype toward production is:

1. Add authentication and origin restrictions.
2. Add request ids and structured graph event correlation.
3. Move ingestion to a background queue with progress state.
4. Separate source originals, chunks, and retrieval indexes.
5. Add deterministic evaluation datasets for retrieval and verification.
6. Add an external embedding provider and Qdrant adapter.
7. Add provider timeouts, retry budgets, circuit breaking, and cost limits.
8. Isolate symbolic and Lean execution in workers.
9. Persist run histories and source snapshots.
10. Add dashboards, alerts, backups, and a disaster-recovery exercise.

This sequence prioritizes control and auditability before model scale. The goal is not just a more fluent answer; it is a system whose answer can be inspected, reproduced, and challenged.

## Known limitations

- The local scorer is lexical and frequency based; it is not an embedding model.
- The fallback provider is deterministic and intentionally narrow.
- The verifier recognizes a small set of claim patterns and does not parse arbitrary equations from prose.
- `/api/documents` has no authentication.
- CORS is open for local development.
- The JSON repository is not designed for concurrent multi-process writers.
- The browser client escapes neither model-generated HTML nor Markdown because it renders answer and source text with `textContent` only in the relevant content areas; future rich rendering must sanitize explicitly.
- There is no user or workspace isolation yet.

These are explicit boundaries, not hidden promises. Each limitation has a corresponding extension path in [docs/architecture.md](docs/architecture.md) and [docs/deployment.md](docs/deployment.md).

## Troubleshooting

### `ModuleNotFoundError`

Use the same interpreter for installation and execution:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m compileall app tests
```

### Empty retrieval results

Run `stats`, confirm the data file exists, and search with terminology likely to occur in a source. Ingest a Markdown or text reference with the CLI, then restart the process if another process has replaced the corpus file.

### Port already in use

Choose a different port:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8010
```

### `.env` appears in Git status

Do not stage it. Check that `.gitignore` contains `.env`, then run `git check-ignore .env`. If the file was already committed historically, ignoring it is not enough; remove it from the index with a deliberate Git operation and rotate any exposed credentials.

## Verification checklist before sharing

```powershell
.\.venv\Scripts\python.exe -m compileall app tests
.\.venv\Scripts\python.exe -m pytest -q
git check-ignore .env
git status --short
```

Then open the application, run one verified Euler query, one partial general proof query, ingest a temporary document, confirm it appears in `stats`, and restore the starter corpus if the temporary document should not ship. This small ritual catches both software regressions and accidental knowledge-base changes.
