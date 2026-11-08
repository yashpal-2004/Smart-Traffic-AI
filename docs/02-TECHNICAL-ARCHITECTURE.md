# Technical Architecture

## Implemented stack

- Python 3.10+ simulation and policy code; no numerical library dependency.
- FastAPI + Pydantic API boundary, served locally by Uvicorn.
- Static, dependency-free HTML/CSS/JavaScript frontend; SVG intersection drawing and Canvas/SVG history visualization.
- `unittest` checks for simulator, policies, evaluation, and API behavior.

## Component boundaries

`backend/app/simulator/` owns seeded arrivals, queues, phases, transitions, movement, and metrics. `agents/` contains fixed-time, hold/switch Q-learning, and green-duration semi-Markov Q-learning policies. `evaluation/` executes matched seeds and returns episode-level results, summaries, paired deltas, and intervals. `api/` validates inputs, manages process-local runs and training, and serializes reports. `traffic_feed.py` reads and normalizes the read-only Brisbane City Council public feed. `traffic_history.py` stores unique timestamp/site observations in local SQLite and evaluates a per-site next-cycle ridge regression against a persistence baseline. `frontend/` renders the user workflow and sends JSON requests; it does not simulate traffic itself.

## Runtime flow

1. The browser sends a run, step, training, or evaluation request to the FastAPI `/api` routes.
2. The API validates the request and invokes the simulator/policy layer.
3. Matched evaluation reuses each scenario/seed pair across the baseline and available learned controllers.
4. The report includes episode rows, per-controller aggregates, paired differences, uncertainty estimates, protocol details, source revision, and hashes of available local checkpoints.
5. JSON and typed-row CSV downloads are created in the browser. The server does not persist evaluation reports.

## State and persistence

Live runs and training progress are in memory and are lost on server restart. Q-table checkpoints are saved locally to ignored `backend/artifacts/q_table.json` and `duration_q_table.json` after successful training. They are not included in a clean clone. Evaluation reports are downloaded by the user and are not uploaded or stored remotely.

Traffic history is stored locally at ignored `backend/data/traffic_history.sqlite3` by default; set `TRAFFIC_HISTORY_DB` to override the path. Start `python3 backend/scripts/collect_traffic_history.py --interval 60 --site-id "YOUR_SITE_ID"` from the repository root to poll one controller site. The API also supports manual capture with `POST /api/traffic/history/collect?site_id=...`; selected-site capture backfills the recent records available for that site. An initial unfiltered snapshot is useful for discovering site IDs. Duplicate source timestamps are ignored. The forecaster requires at least 24 unique observations for a site.

## Evaluation contract

- Scenarios: balanced, rush hour, and northbound surge, each with a fixed per-approach Bernoulli arrival probability.
- Seeds are matched across controllers within each selected scenario.
- Wait: average queueing seconds among vehicles served during an episode.
- Queue: mean queued vehicles observed after each simulation step.
- Throughput: vehicles served in the episode.
- Paired intervals: two-sided 95% t intervals for paired differences, with a normal approximation above 30 observations; unavailable for one observation. Pooled intervals combine selected scenarios; scenario-level summaries are also returned.

## API

- `GET /api/health`, `GET /api/scenarios`, `GET /api/simulators`, `GET /api/model`
- `POST /api/runs`; `GET /api/runs/{id}`; `DELETE /api/runs/{id}`; `POST /api/runs/{id}/step`
- `POST /api/runs/{id}/control/{pause|resume|reset}`
- `POST /api/training`; `GET /api/training`
- `POST /api/evaluations`
- `GET /api/traffic/live` (read-only public sensor summaries; upstream errors return 503)
- `POST /api/traffic/history/collect`; `GET /api/traffic/history`; `GET /api/traffic/forecast?site_id=...`

See FastAPI's generated `/docs` page while the service is running for request and response schemas.

## Constraints

The simulator remains an educational single-intersection model and is not for real-world signal control. The city feed is observational only: measured flow is per signal-controller cycle, detector occupancy is a percentage, and opaque lane identifiers are not mapped to the simulator's compass approaches. The Brisbane dataset covers only intersections operated by Brisbane City Council and is subject to upstream availability. Forecasts are one source cycle ahead, not hourly demand forecasts. The first 24-observation site evaluation is documented in `docs/sample-evaluation/traffic-forecast-site-102.json`; its 5-point holdout favored persistence over ridge regression, so it supports no model-improvement claim. Forecasted aggregate site counts are not currently used as directional simulator arrivals. The app has no authentication, multi-user isolation, control connection to signals, or production deployment configuration. For deployments without Git metadata, `SMART_TRAFFIC_SOURCE_REVISION` can supply the source identifier recorded in evaluation metadata.

## Optional SUMO runtime and evaluation backend

`backend/app/simulator/sumo/` contains the four-way network source and TraCI adapter. `GET /api/simulators` reports whether SUMO, `sumo-gui`, its graphical display, and a current-version SUMO-trained policy are available. `POST /api/runs` accepts `engine: "python"` or `engine: "sumo"`; both engines return the same live snapshot fields to the dashboard. SUMO snapshots additionally include vehicle front-bumper coordinates and headings, network and junction bounds, and per-approach signal states. The frontend uses those bounds to align vehicles and stop lines with the drawn network. SUMO queues and rewards include both halted inbound vehicles and generated vehicles pending insertion, and evaluation reports include pending-at-end and generated-demand counts. Signal greens are assigned from TraCI controlled links so only the two opposing approaches in the active phase receive green. The Simulate page can switch engines and closes the old run before creating the new one. When selected, the optional desktop viewer launches `sumo-gui` and receives the same TraCI-controlled steps as the dashboard. On macOS, XQuartz must be installed and opened before starting the backend; when desktop graphics are unavailable, the dashboard remains a live view of SUMO and displays the reason. SUMO fixed-time control is available after installing the optional dependencies. SUMO hold/switch Q-learning uses `backend/artifacts/sumo_q_table.json`, created by `backend/scripts/run_sumo_evaluation.py`; the checkpoint is versioned and must be retrained after network or signal-model changes. The evaluation runner trains on distinct scenario/seed draws, then evaluates fixed-time and learned policies on matched seeds. Install `eclipse-sumo` and `traci` from `backend/requirements-sumo.txt`; the `sumo` and `netconvert` executables must be on `PATH` or included in the Eclipse SUMO package.
