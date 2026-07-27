# SWE-Onboarding

Simple support ticket microservice with:
- CRUD APIs for tickets
- Azure Cosmos DB integration (with local in-memory fallback)
- CI/CD pipeline (GitHub Actions + optional Azure deploy)
- Basic observability (request logging + health endpoint)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
uvicorn app.main:app --reload
```

API docs are available at `http://127.0.0.1:8000/docs`.

## Cosmos DB configuration

Set these environment variables to use Azure Cosmos DB:
- `COSMOS_DB_ENDPOINT`
- `COSMOS_DB_KEY`
- `COSMOS_DB_NAME` (optional, default: `support`)
- `COSMOS_CONTAINER_NAME` (optional, default: `tickets`)

If endpoint/key are not set (or Cosmos initialization fails), the service falls back to in-memory storage.

## Test

```bash
pytest -q
```