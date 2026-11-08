# Backend

## Install and run API

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload
```

API docs: http://127.0.0.1:8000/docs

## Checks

```sh
PYTHONPATH=backend python3 -m unittest discover -s backend/tests -v
```

## Train and evaluate

```sh
PYTHONPATH=backend python3 backend/scripts/train_and_evaluate.py --episodes 1000 --steps 500
```

Evaluation is performed on held-out seeds and writes a JSON report plus a local Q-table under `backend/artifacts/`.

The simulator is simplified: one vehicle per active approach may clear each second, with two opposing signal phases and Bernoulli vehicle arrivals. It is for learning, not real-world signal operation.
