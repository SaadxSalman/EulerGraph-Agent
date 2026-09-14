# Deployment and Operations

## Local development

Use the venv interpreter directly on Windows when activation policies are restrictive:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The service binds to localhost by default. This is deliberate: the ingestion endpoint has no authentication yet.

## Docker

Build and run:

```powershell
docker build -t eulergraph-agent .
docker run --rm -p 8000:8000 --env-file .env eulergraph-agent
```

The image copies the application, web client, starter corpus, metadata, and README. It does not copy `.env` because `.dockerignore` excludes it.

For persistent indexing, mount a volume at `/opt/eulergraph/data`. A production image should use a non-root user and pin dependencies using a lock file.

## Environment policy

There is one local `.env` file in this repository and no example file by design. It is ignored by Git. Required operational variables are:

- `APP_NAME`: display and API title.
- `ENVIRONMENT`: development, staging, or production label.
- `API_HOST` and `API_PORT`: bind settings used by the launch command.
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`: server-only provider credentials.
- `QDRANT_URL`, `QDRANT_API_KEY`: optional vector store credentials.
- `EMBEDDING_MODEL`, `LLM_MODEL`: provider model identifiers.
- `DATA_DIR`: local corpus location.
- `MAX_RETRIEVAL_RESULTS`: evidence limit per solve.

At deployment time, inject secrets through the platform secret manager and keep the repository `.env` empty or development-only. Never expose an API key to `web/app.js`.

## Reverse proxy checklist

Put the app behind a TLS-terminating reverse proxy before sharing it:

- Restrict CORS to the known frontend origin.
- Enforce request body and timeout limits.
- Require authentication for `/api/documents`.
- Add rate limiting to `/api/solve`.
- Forward a request id and include it in structured logs.
- Disable or protect `/docs` in sensitive environments.
- Configure health checks against `/api/health`.

## Observability

`app/observability.py` provides a JSON formatter and a `timed_event` context manager. The current graph uses response durations for the client trace. The next operational step is to wrap each graph node in an event with a correlation id, source count, provider name, and verification result. Do not log full private documents or prompts by default.

Useful metrics:

- Solve requests by route intent.
- Retrieval hit rate and top-score distribution.
- Provider latency and error rate.
- Verification status distribution.
- Corpus document count and average chunk length.
- Ingestion failures by file type.

## Backup and recovery

The starter system persists to `data/documents.json`. Back it up before bulk ingestion. For production, store originals separately from chunks and make indexing repeatable from originals. A rebuild should be possible without losing provenance or manually edited metadata.

## Security model

The current project is a development-grade local service. It intentionally lacks users, permissions, and arbitrary code execution. Never add an endpoint that evaluates model-produced Python in the API process. Symbolic verification should remain allow-listed and resource constrained. A Lean compiler should run in a separate worker with CPU, memory, filesystem, and wall-clock limits.
