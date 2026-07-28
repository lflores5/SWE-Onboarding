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

## CI/CD Pipeline

This project includes a comprehensive GitHub Actions CI pipeline that runs on every pull request and push to `main`.

### CI Jobs

1. **Linting and Code Quality** (`lint_and_quality`)
   - **Flake8**: Python linting to catch syntax errors and style issues
   - **Bandit**: Security vulnerability scanning
   - **Black**: Code formatting verification

2. **Testing** (`run_tests`)
   - Runs all pytest tests with verbose output
   - Only runs if linting passes

3. **Docker Build** (`build_docker_image`)
   - Builds the Docker container image
   - Verifies the image works correctly
   - Only runs if tests pass

### Running Linting Locally

Before pushing code, you can run the same checks locally:

```bash
# Install linting tools (included in requirements.txt)
pip install -r requirements.txt

# Run flake8
flake8 . --max-line-length=120 --exclude=.venv,swe_onboarding_tickets.egg-info

# Run bandit (security checks)
bandit -r app/ -ll

# Check code formatting with black
black --check app/ tests/

# Auto-format code with black
black app/ tests/
```

### Setting Up Branch Protection

To enforce CI checks before merging:

1. Go to your GitHub repository → **Settings** → **Branches**
2. Add a branch protection rule for `main`:
   - ✅ Require status checks to pass before merging
   - Select required checks:
     - `lint_and_quality`
     - `run_tests`
     - `build_docker_image`
   - ✅ Require branches to be up to date before merging
3. Save the rule

Now all pull requests must pass CI checks before they can be merged!