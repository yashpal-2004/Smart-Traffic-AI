# Signal Lab frontend

Dependency-free static HTML, CSS, and JavaScript client for the Smart Traffic AI API. No npm install or build step is needed.

From the repository root:

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory frontend
```

Start the API separately using the instructions in [`backend/README.md`](../backend/README.md), then open [http://127.0.0.1:4173](http://127.0.0.1:4173). The default API URL is `http://127.0.0.1:8000/api`. Set `window.TRAFFIC_API_URL` before `app.js` loads to point the UI at a different API; configure matching CORS origins in the backend for non-local hosting.
