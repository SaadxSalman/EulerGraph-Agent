# Contributing

## Development loop

1. Create or activate the workspace virtual environment.
2. Install `requirements.txt`.
3. Run `python -m compileall app tests`.
4. Run `python -m pytest -q`.
5. Start Uvicorn and manually exercise the browser workspace.
6. Check `git diff` and confirm `.env` remains ignored.

## Style

Use type annotations on public functions, keep Pydantic models at transport boundaries, and prefer small pure functions for routing, scoring, parsing, and verification. Avoid adding a dependency when a standard-library solution is clear and testable.

## Tests

Every new routing rule should have a router test. Retrieval changes should test ranking and empty results. Verification changes should test both a successful check and a conservative failure or partial path. API changes should assert response shape rather than fragile prose formatting.

## Adding a provider

Implement the provider behind the existing async method. Keep remote imports optional when possible so local installation remains lightweight. Return plain answer text to the graph and attach provider metadata through a future structured provider result rather than embedding network details in the UI.

## Adding corpus material

Use the ingestion endpoint or CLI. Preserve citation information in the title and author fields, and keep one concept per chunk where possible. Do not add private or copyrighted source material to a public repository.

## Pull request checklist

- [ ] Tests cover the changed behavior.
- [ ] No secrets or generated environments are included.
- [ ] Public response models are updated if the contract changed.
- [ ] README or docs explain new configuration.
- [ ] `compileall` and `pytest` pass.
- [ ] Security implications of new execution paths are documented.
