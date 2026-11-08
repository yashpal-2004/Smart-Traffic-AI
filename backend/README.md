# Backend

FastAPI service for the deterministic traffic simulator, local tabular-policy training, and matched-seed evaluation.

## Install and run

From the repository root (Python 3.10+):

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
PYTHONPATH=backend python -m uvicorn app.main:app --app-dir backend --reload
```

The API listens on `http://127.0.0.1:8000`; interactive docs are at `/docs`. Start the static frontend separately with `python3 -m http.server 4173 --bind 127.0.0.1 --directory frontend` from the repository root.

## Endpoints

- `GET /api/health`, `GET /api/scenarios`, `GET /api/model`
- `POST /api/runs`, `GET /api/runs/{id}`, `POST /api/runs/{id}/step`
- `POST /api/runs/{id}/control/{pause|resume|reset}`
- `POST /api/training`, `GET /api/training`
- `POST /api/evaluations`

Run state and training-job progress are held in memory. Completed Q-tables are stored in ignored local files under `backend/artifacts/`; a clean clone therefore starts without learned checkpoints. Evaluation reports contain matched seeds, paired deltas, intervals, scenario arrival rates, checkpoint hashes, and source metadata.

For deployments without a `.git` directory, set `SMART_TRAFFIC_SOURCE_REVISION` to the source commit identifier. If Git metadata is unavailable and no override is set, the report marks the source revision unavailable.

## Optional checks

```sh
PYTHONPATH=backend python3 -m unittest discover -s backend/tests -v
```
