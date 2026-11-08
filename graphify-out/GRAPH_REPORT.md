# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 26 files · ~6,903 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .css 1)

## Summary
- 206 nodes · 422 edges · 22 communities (13 shown, 9 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 43 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5a84544b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QLearningAgent
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
- environment.py

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 37 edges
2. `QLearningAgent` - 27 edges
3. `SignalConfig` - 24 edges
4. `train_episode()` - 17 edges
5. `FixedTimeController` - 14 edges
6. `evaluate()` - 13 edges
7. `Scenario` - 12 edges
8. `SimulatorTests` - 12 edges
9. `run_episode()` - 12 edges
10. `Phase` - 10 edges

## Surprising Connections (you probably didn't know these)
- `QLearningAgent` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/app/agents/q_learning.py → backend/app/simulator/environment.py
- `evaluate()` --uses--> `QLearningAgent`  [INFERRED]
  backend/app/evaluation/runner.py → backend/app/agents/q_learning.py
- `run_episode()` --uses--> `QLearningAgent`  [INFERRED]
  backend/app/evaluation/runner.py → backend/app/agents/q_learning.py
- `EvaluationTests` --uses--> `QLearningAgent`  [INFERRED]
  backend/tests/test_evaluation.py → backend/app/agents/q_learning.py
- `FixedTimeController` --uses--> `Phase`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (22 total, 9 thin omitted)

### Community 0 - "QLearningAgent"
Cohesion: 0.16
Nodes (5): observe(), QLearningAgent, train_episode(), train_model(), QLearningTests

### Community 1 - "TrafficEnvironment"
Cohesion: 0.19
Nodes (7): FixedTimeController, run_episode(), Metrics, Scenario, Snapshot, TrafficEnvironment, SimulatorTests

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
Cohesion: 0.14
Nodes (13): control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), health(), model_status(), Run (+5 more)

### Community 7 - "AI Agent Handoff Instructions"
Cohesion: 0.40
Nodes (4): AI Agent Handoff Instructions, Handoff note template, Rules, YYYY-MM-DD — Milestone / task

### Community 8 - "Decisions and Progress Log"
Cohesion: 0.20
Nodes (9): 2026-11-08 — M1 deterministic simulator complete, 2026-11-08 — M2 Q-learning core implemented, 2026-11-08 — M3 demand review, M4 API, M5 visual dashboard, 2026-11-08 — M3 evaluation runner implemented, 2026-11-08 — Planning files created, 2026-11-08 — Trainable model and live history, Decisions, Decisions and Progress Log (+1 more)

### Community 9 - "Smart Traffic AI"
Cohesion: 0.50
Nodes (3): Current status, Smart Traffic AI, Start here

### Community 10 - "Backend"
Cohesion: 0.40
Nodes (4): Backend, Checks, Install and run API, Train and evaluate

### Community 14 - "QLearningAgent"
Cohesion: 0.19
Nodes (8): run_evaluation(), EpisodeResult, evaluate(), summarize(), write_report(), SignalConfig, main(), EvaluationTests

### Community 17 - "app.js"
Cohesion: 0.38
Nodes (11): createRun(), doStep(), drawCars(), drawHistory(), pause(), phaseName(), request(), runLoop() (+3 more)

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `QLearningAgent`, `environment.py`, `routes.py`, `QLearningAgent`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `observe()`) actually correct?**
  _`TrafficEnvironment` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14130434782608695 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `TrafficEnvironment`, `routes.py`, `QLearningAgent`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `QLearningAgent` (e.g. with `TrafficEnvironment` and `evaluate()`) actually correct?**
  _`QLearningAgent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `train_episode()` (e.g. with `.act()` and `.end_episode()`) actually correct?**
  _`train_episode()` has 7 INFERRED edges - model-reasoned connections that need verification._