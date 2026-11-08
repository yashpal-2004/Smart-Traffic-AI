# Technical Architecture

## Implemented stack

- Python 3.10+ simulation and policy code; no numerical library dependency.
- FastAPI + Pydantic API boundary, served locally by Uvicorn.
- Static, dependency-free HTML/CSS/JavaScript frontend; SVG intersection drawing and Canvas/SVG history visualization.
- `unittest` checks for simulator, policies, evaluation, and API behavior.

## Component boundaries

`backend/app/simulator/` owns seeded arrivals, queues, phases, transitions, movement, and metrics. `agents/` contains fixed-time, hold/switch Q-learning, and green-duration semi-Markov Q-learning policies. `evaluation/` executes matched seeds and returns episode-level results, summaries, paired deltas, and intervals. `api/` validates inputs, manages process-local runs and training, and serializes reports. `frontend/` renders the user workflow and sends JSON requests; it does not simulate traffic itself.

## Runtime flow

1. The browser sends a run, step, training, or evaluation request to the FastAPI `/api` routes.
2. The API validates the request and invokes the simulator/policy layer.
3. Matched evaluation reuses each scenario/seed pair across the baseline and available learned controllers.
4. The report includes episode rows, per-controller aggregates, paired differences, uncertainty estimates, protocol details, source revision, and hashes of available local checkpoints.
5. JSON and typed-row CSV downloads are created in the browser. The server does not persist evaluation reports.

## State and persistence

Live runs and training progress are in memory and are lost on server restart. Q-table checkpoints are saved locally to ignored `backend/artifacts/q_table.json` and `duration_q_table.json` after successful training. They are not included in a clean clone. Evaluation reports are downloaded by the user and are not uploaded or stored remotely.

## Evaluation contract

- Scenarios: balanced, rush hour, and northbound surge, each with a fixed per-approach Bernoulli arrival probability.
- Seeds are matched across controllers within each selected scenario.
- Wait: average queueing seconds among vehicles served during an episode.
- Queue: mean queued vehicles observed after each simulation step.
- Throughput: vehicles served in the episode.
- Paired intervals: two-sided 95% t intervals for paired differences, with a normal approximation above 30 observations; unavailable for one observation. Pooled intervals combine selected scenarios; scenario-level summaries are also returned.

## API

- `GET /api/health`, `GET /api/scenarios`, `GET /api/model`
- `POST /api/runs`; `GET /api/runs/{id}`; `POST /api/runs/{id}/step`
- `POST /api/runs/{id}/control/{pause|resume|reset}`
- `POST /api/training`; `GET /api/training`
- `POST /api/evaluations`

See FastAPI's generated `/docs` page while the service is running for request and response schemas.

## Constraints

This is an educational single-intersection model and is not for real-world signal control. It has no authentication, database, multi-user isolation, external telemetry, or production deployment configuration. For deployments without Git metadata, `SMART_TRAFFIC_SOURCE_REVISION` can supply the source identifier recorded in evaluation metadata.
