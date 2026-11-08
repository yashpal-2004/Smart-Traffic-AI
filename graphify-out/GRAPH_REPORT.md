# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 28 files · ~9,831 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .css 1)

## Summary
- 237 nodes · 510 edges · 22 communities (13 shown, 9 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6c86588e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TrafficEnvironment
- Product, Pages, and Premium UI Direction
- Milestones and Acceptance Checks
- Project Brief
- Technical Architecture
- routes.py
- AI Agent Handoff Instructions
- Decisions and Progress Log
- Smart Traffic AI
- Backend
- QLearningAgent
- ApiTests
- app.js
- frontend/README.md
- SignalConfig

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 42 edges
2. `QLearningAgent` - 28 edges
3. `SignalConfig` - 28 edges
4. `train_episode()` - 19 edges
5. `Progress` - 18 edges
6. `evaluate()` - 17 edges
7. `DurationQLearningAgent` - 15 edges
8. `train_duration_episode()` - 15 edges
9. `FixedTimeController` - 14 edges
10. `run_episode()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `FixedTimeController` --uses--> `Phase`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `Approach`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `Phase`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `SignalConfig`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (22 total, 9 thin omitted)

### Community 0 - "TrafficEnvironment"
Cohesion: 0.12
Nodes (9): FixedTimeController, observe(), train_episode(), run_episode(), Metrics, Scenario, Snapshot, TrafficEnvironment (+1 more)

### Community 2 - "Product, Pages, and Premium UI Direction"
Cohesion: 0.18
Nodes (10): About page, Accessibility, Compare page, Information architecture, Interaction and states, Learn page, Product, Pages, and Premium UI Direction, Simulate page (primary) (+2 more)

### Community 3 - "Milestones and Acceptance Checks"
Cohesion: 0.20
Nodes (9): M0 — Documentation and decisions (DONE), M1 — Deterministic simulator core (DONE), M2 — Q-learning agent (IN PROGRESS), M3 — Evaluation and evidence (IN PROGRESS), M4 — Backend API (DONE), M5 — Premium frontend (IN PROGRESS), M6 — Polish and release (NOT STARTED), Milestones and Acceptance Checks (+1 more)

### Community 4 - "Project Brief"
Cohesion: 0.22
Nodes (8): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria

### Community 5 - "Technical Architecture"
Cohesion: 0.22
Nodes (8): API sketch, Component boundaries, Data and reproducibility, Engineering constraints, Proposed stack, Simulator contract, Suggested repo layout, Technical Architecture

### Community 6 - "routes.py"
Cohesion: 0.13
Nodes (15): control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), health(), model_status(), Run (+7 more)

### Community 7 - "AI Agent Handoff Instructions"
Cohesion: 0.40
Nodes (4): AI Agent Handoff Instructions, Handoff note template, Rules, YYYY-MM-DD — Milestone / task

### Community 8 - "Decisions and Progress Log"
Cohesion: 0.10
Nodes (20): 2026-11-08 — Background training progress, 2026-11-08 — Browser check of trained comparison, 2026-11-08 — Comparison reporting and CSV export, 2026-11-08 — Configurable paired-seed evaluation, 2026-11-08 — Configurable training and policy guide, 2026-11-08 — Duration policy in live simulation, 2026-11-08 — Full evaluation report CSV, 2026-11-08 — Green-duration semi-Markov agent (+12 more)

### Community 9 - "Smart Traffic AI"
Cohesion: 0.50
Nodes (3): Current status, Smart Traffic AI, Start here

### Community 10 - "Backend"
Cohesion: 0.40
Nodes (4): Backend, Checks, Install and run API, Train and evaluate

### Community 14 - "QLearningAgent"
Cohesion: 0.14
Nodes (12): DurationQLearningAgent, train_duration_episode(), QLearningAgent, run_evaluation(), worker(), evaluate(), write_report(), SignalConfig (+4 more)

### Community 17 - "app.js"
Cohesion: 0.32
Nodes (14): createRun(), doStep(), drawCars(), drawHistory(), exportEpisodes(), intervalLabel(), pause(), phaseName() (+6 more)

### Community 21 - "SignalConfig"
Cohesion: 0.17
Nodes (5): EpisodeResult, paired_delta_summary(), summarize(), Approach, Phase

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `SignalConfig`, `QLearningAgent`, `routes.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `TrafficEnvironment` be split into smaller, more focused modules?**
  _Cohesion score 0.12435897435897436 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `TrafficEnvironment`, `SignalConfig`, `routes.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1282051282051282 - nodes in this community are weakly interconnected._
- **Are the 6 inferred relationships involving `train_episode()` (e.g. with `.act()` and `.end_episode()`) actually correct?**
  _`train_episode()` has 6 INFERRED edges - model-reasoned connections that need verification._