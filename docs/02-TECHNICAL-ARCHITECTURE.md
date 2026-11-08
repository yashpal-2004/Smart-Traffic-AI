# Technical Architecture

## Proposed stack
- Python 3.11+ core simulation and learning logic.
- NumPy for numeric utilities; start with a small custom discrete simulator.
- FastAPI backend to expose scenario, run, step, training, and evaluation APIs.
- React + TypeScript + Vite frontend; SVG or Canvas for intersection visualization; a chart library selected during implementation.
- Pydantic schemas at API boundaries; pytest for deterministic simulator and policy tests; frontend lint/build checks.
- Docker Compose optional for one-command local startup after basic local development works.

## Component boundaries
`simulator/` owns world state, vehicle arrivals, phase transitions, movement, metrics, and seeded randomness. It must not depend on web/UI libraries.

`agents/` owns policy interface, fixed-time policy, random policy for debugging, Q-learning table, epsilon schedule, and persistence format.

`evaluation/` runs policies over matched scenario/seed sets, aggregates metrics, and emits machine-readable results.

`api/` validates requests, manages in-memory runs for v1, and translates domain objects to DTOs. Keep simulation logic out of route handlers.

`web/` contains pages, controls, visualization, charts, and API client. It must not reimplement traffic or reward rules.

`docs/` is the durable source of truth for requirements, decisions, milestones, and agent continuity.

## Suggested repo layout
```
backend/
  app/main.py
  app/api/routes/
  app/simulator/{environment,vehicles,signals,scenarios,metrics}.py
  app/agents/{base,fixed_time,q_learning}.py
  app/evaluation/{runner,report}.py
  tests/
frontend/
  src/{app,pages,components,features,lib,styles}/
docs/
```

## Simulator contract
- Four approaches: N, E, S, W; fixed capacity queues.
- Discrete simulation step (initially 1 second); arrival probabilities/rates per approach.
- Signal phase serves one non-conflicting pair (N/S or E/W); minimum green, maximum green, and amber/all-red transition are explicit.
- A step deterministically: apply phase transition, generate arrivals from seeded RNG, move eligible vehicles, update waits/queues/throughput, calculate observation/reward, return snapshot.
- Observation v1: bounded queue sizes per approach, current phase, and elapsed green bucket. Keep state small enough for tabular Q-learning.
- Action v1: hold current phase or request switch, subject to minimum green and safe transition.
- Reward v1: penalize total waiting/queue and switching overhead; reward throughput only if experiments show it does not encourage unstable switching. Document and test exact formula.
- Baseline: fixed-time phases with the same transition rules.

## API sketch
- `GET /api/scenarios` -> scenario catalog.
- `POST /api/runs` -> create run with policy/scenario/seed/config.
- `POST /api/runs/{id}/step` -> advance N steps and return snapshot.
- `POST /api/runs/{id}/control` -> pause/resume/reset where applicable.
- `GET /api/runs/{id}` -> snapshot and metrics.
- `POST /api/evaluations` -> matched batch evaluation request.
- `GET /api/evaluations/{id}` -> status and results.
Use WebSocket only if polling/step responses prove inadequate; avoid premature complexity.

## Data and reproducibility
Each run stores config, seed, policy name/version, simulator version, metrics, and step trace. Evaluation creates paired runs with identical arrival seeds for each controller. Training episodes and held-out evaluation seeds remain separate. Export summary data in JSON/CSV.

## Engineering constraints
No arbitrary repository code is executed. No external telemetry by default. Bound request sizes and run duration. Surface exceptions as actionable UI errors; log server details without leaking secrets.
