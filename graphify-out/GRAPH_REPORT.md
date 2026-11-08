# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 28 files · ~11,771 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .css 1)

## Summary
- 255 nodes · 541 edges · 16 communities (8 shown, 8 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 45 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0ba163ca`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TrafficEnvironment
- Product, Pages, and Premium UI Direction
- Milestones and Acceptance Checks
- routes.py
- Decisions and Progress Log
- Backend
- ApiTests
- app.js
- SignalConfig

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 42 edges
2. `QLearningAgent` - 28 edges
3. `SignalConfig` - 28 edges
4. `Progress` - 22 edges
5. `train_episode()` - 19 edges
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
- `FixedTimeController` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `create_run()` --calls--> `FixedTimeController`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/agents/fixed_time.py
- `SimulatorTests` --uses--> `FixedTimeController`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/agents/fixed_time.py

## Import Cycles
- None detected.

## Communities (16 total, 8 thin omitted)

### Community 0 - "TrafficEnvironment"
Cohesion: 0.15
Nodes (10): FixedTimeController, run_episode(), Approach, Metrics, Phase, Scenario, SignalConfig, Snapshot (+2 more)

### Community 2 - "Product, Pages, and Premium UI Direction"
Cohesion: 0.18
Nodes (10): About page, Accessibility, Compare page, Information architecture, Interaction and states, Learn page, Product, Pages, and Premium UI Direction, Simulate page (primary) (+2 more)

### Community 4 - "Milestones and Acceptance Checks"
Cohesion: 0.05
Nodes (37): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria (+29 more)

### Community 6 - "routes.py"
Cohesion: 0.10
Nodes (17): control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), health(), model_status(), Run (+9 more)

### Community 8 - "Decisions and Progress Log"
Cohesion: 0.08
Nodes (24): 2026-11-08 — Background training progress, 2026-11-08 — Browser check of trained comparison, 2026-11-08 — Comparison reporting and CSV export, 2026-11-08 — Configurable paired-seed evaluation, 2026-11-08 — Configurable training and policy guide, 2026-11-08 — Duration policy in live simulation, 2026-11-08 — Full evaluation report CSV, 2026-11-08 — Green-duration semi-Markov agent (+16 more)

### Community 10 - "Backend"
Cohesion: 0.29
Nodes (5): Backend, Endpoints, Install and run, Optional checks, Signal Lab frontend

### Community 17 - "app.js"
Cohesion: 0.27
Nodes (17): createRun(), doStep(), downloadReport(), drawCars(), drawHistory(), exportEpisodes(), exportReportJson(), intervalLabel() (+9 more)

### Community 21 - "SignalConfig"
Cohesion: 0.09
Nodes (15): DurationQLearningAgent, train_duration_episode(), observe(), QLearningAgent, train_episode(), worker(), EpisodeResult, evaluate() (+7 more)

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `SignalConfig`, `routes.py`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `TrafficEnvironment` be split into smaller, more focused modules?**
  _Cohesion score 0.145748987854251 - nodes in this community are weakly interconnected._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Milestones and Acceptance Checks` be split into smaller, more focused modules?**
  _Cohesion score 0.047619047619047616 - nodes in this community are weakly interconnected._
- **Are the 6 inferred relationships involving `train_episode()` (e.g. with `.act()` and `.end_episode()`) actually correct?**
  _`train_episode()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09803921568627451 - nodes in this community are weakly interconnected._