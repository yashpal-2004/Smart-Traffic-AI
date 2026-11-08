# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 31 files · ~15,261 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 1, .csv 1, .css 1)

## Summary
- 272 nodes · 566 edges · 18 communities (8 shown, 10 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 45 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a0f6fdcf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TrafficEnvironment
- Product, Pages, and Premium UI Direction
- sample-evaluation/README.md
- Milestones and Acceptance Checks
- routes.py
- Decisions and Progress Log
- Backend
- ApiTests
- app.js
- SignalConfig

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 42 edges
2. `SignalConfig` - 28 edges
3. `QLearningAgent` - 28 edges
4. `Progress` - 25 edges
5. `train_episode()` - 19 edges
6. `evaluate()` - 17 edges
7. `DurationQLearningAgent` - 15 edges
8. `train_duration_episode()` - 15 edges
9. `FixedTimeController` - 14 edges
10. `run_episode()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `SignalConfig`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `create_run()` --calls--> `FixedTimeController`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/agents/fixed_time.py
- `create_run()` --calls--> `SignalConfig`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/simulator/environment.py
- `create_run()` --calls--> `TrafficEnvironment`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (18 total, 10 thin omitted)

### Community 0 - "TrafficEnvironment"
Cohesion: 0.15
Nodes (9): FixedTimeController, run_episode(), Approach, Metrics, Phase, Scenario, Snapshot, TrafficEnvironment (+1 more)

### Community 2 - "Product, Pages, and Premium UI Direction"
Cohesion: 0.18
Nodes (10): About page, Accessibility, Compare page, Information architecture, Interaction and states, Learn page, Product, Pages, and Premium UI Direction, Simulate page (primary) (+2 more)

### Community 4 - "Milestones and Acceptance Checks"
Cohesion: 0.05
Nodes (38): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria (+30 more)

### Community 6 - "routes.py"
Cohesion: 0.08
Nodes (20): control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), health(), live_traffic(), model_status() (+12 more)

### Community 8 - "Decisions and Progress Log"
Cohesion: 0.07
Nodes (27): 2026-11-08 — Background training progress, 2026-11-08 — Browser check of trained comparison, 2026-11-08 — Comparison reporting and CSV export, 2026-11-08 — Configurable paired-seed evaluation, 2026-11-08 — Configurable training and policy guide, 2026-11-08 — Duration policy in live simulation, 2026-11-08 — Full evaluation report CSV, 2026-11-08 — Green-duration semi-Markov agent (+19 more)

### Community 10 - "Backend"
Cohesion: 0.29
Nodes (5): Backend, Endpoints, Install and run, Optional checks, Signal Lab frontend

### Community 17 - "app.js"
Cohesion: 0.24
Nodes (19): createRun(), doStep(), downloadReport(), drawCars(), drawHistory(), exportEpisodes(), exportReportJson(), formatFeedAge() (+11 more)

### Community 21 - "SignalConfig"
Cohesion: 0.10
Nodes (16): DurationQLearningAgent, train_duration_episode(), observe(), QLearningAgent, train_episode(), worker(), EpisodeResult, evaluate() (+8 more)

## Knowledge Gaps
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `.act`, `SignalConfig`, `routes.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `TrafficEnvironment` be split into smaller, more focused modules?**
  _Cohesion score 0.146218487394958 - nodes in this community are weakly interconnected._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Milestones and Acceptance Checks` be split into smaller, more focused modules?**
  _Cohesion score 0.046511627906976744 - nodes in this community are weakly interconnected._
- **Are the 6 inferred relationships involving `train_episode()` (e.g. with `.act()` and `.end_episode()`) actually correct?**
  _`train_episode()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07641196013289037 - nodes in this community are weakly interconnected._