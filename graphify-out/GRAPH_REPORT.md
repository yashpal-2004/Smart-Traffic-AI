# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 26 files · ~7,327 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .css 1)

## Summary
- 213 nodes · 432 edges · 21 communities (13 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 45 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd54e91b`
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
- `run_episode()` --uses--> `QLearningAgent`  [INFERRED]
  backend/app/evaluation/runner.py → backend/app/agents/q_learning.py
- `observe()` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/app/agents/q_learning.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `Phase`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (21 total, 8 thin omitted)

### Community 0 - "TrafficEnvironment"
Cohesion: 0.15
Nodes (8): FixedTimeController, train_episode(), run_episode(), Metrics, Scenario, Snapshot, TrafficEnvironment, SimulatorTests

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
Cohesion: 0.12
Nodes (16): control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), health(), model_status(), Run (+8 more)

### Community 7 - "AI Agent Handoff Instructions"
Cohesion: 0.40
Nodes (4): AI Agent Handoff Instructions, Handoff note template, Rules, YYYY-MM-DD — Milestone / task

### Community 8 - "Decisions and Progress Log"
Cohesion: 0.17
Nodes (11): 2026-11-08 — Background training progress, 2026-11-08 — Comparison reporting and CSV export, 2026-11-08 — M1 deterministic simulator complete, 2026-11-08 — M2 Q-learning core implemented, 2026-11-08 — M3 demand review, M4 API, M5 visual dashboard, 2026-11-08 — M3 evaluation runner implemented, 2026-11-08 — Planning files created, 2026-11-08 — Trainable model and live history (+3 more)

### Community 9 - "Smart Traffic AI"
Cohesion: 0.50
Nodes (3): Current status, Smart Traffic AI, Start here

### Community 10 - "Backend"
Cohesion: 0.40
Nodes (4): Backend, Checks, Install and run API, Train and evaluate

### Community 14 - "QLearningAgent"
Cohesion: 0.15
Nodes (8): QLearningAgent, run_evaluation(), evaluate(), write_report(), SignalConfig, main(), EvaluationTests, QLearningTests

### Community 17 - "app.js"
Cohesion: 0.35
Nodes (13): createRun(), doStep(), drawCars(), drawHistory(), exportEpisodes(), pause(), phaseName(), renderReport() (+5 more)

### Community 21 - "environment.py"
Cohesion: 0.16
Nodes (5): observe(), EpisodeResult, summarize(), Approach, Phase

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `environment.py`, `QLearningAgent`, `routes.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `observe()`) actually correct?**
  _`TrafficEnvironment` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `TrafficEnvironment` be split into smaller, more focused modules?**
  _Cohesion score 0.14795008912655971 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `TrafficEnvironment`, `environment.py`, `routes.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `QLearningAgent` (e.g. with `TrafficEnvironment` and `evaluate()`) actually correct?**
  _`QLearningAgent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12169312169312169 - nodes in this community are weakly interconnected._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._