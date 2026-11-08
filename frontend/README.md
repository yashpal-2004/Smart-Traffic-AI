# Signal Lab frontend

Static, dependency-free web UI for the Smart Traffic AI API.

Run from the repository root:

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory frontend
```

In a second terminal, start the API:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload
```

Open http://127.0.0.1:4173. The backend uses http://127.0.0.1:8000 and allows the local frontend origin. For a different frontend URL, set `window.TRAFFIC_API_URL` in `app.js` or adjust API CORS configuration.
