# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 33 files · ~17,740 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 1, .csv 1, .css 1)

## Summary
- 309 nodes · 667 edges · 19 communities (10 shown, 9 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 47 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `58743dbc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QLearningAgent
- traffic_history.py
- Product, Pages, and Premium UI Direction
- sample-evaluation/README.md
- Milestones and Acceptance Checks
- collect_traffic_history.py
- routes.py
- Decisions and Progress Log
- Backend
- ApiTests
- app.js
- TrafficEnvironment

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 42 edges
2. `QLearningAgent` - 28 edges
3. `SignalConfig` - 28 edges
4. `Progress` - 26 edges
5. `train_episode()` - 19 edges
6. `evaluate()` - 17 edges
7. `DurationQLearningAgent` - 15 edges
8. `train_duration_episode()` - 15 edges
9. `FixedTimeController` - 14 edges
10. `run_episode()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `live_traffic()` --calls--> `fetch_live_intersections()`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/traffic_feed.py
- `collect_traffic_history()` --calls--> `history_summary()`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/traffic_history.py
- `get_traffic_forecast()` --calls--> `forecast_site()`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/traffic_history.py
- `create_run()` --calls--> `FixedTimeController`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/agents/fixed_time.py
- `create_run()` --calls--> `SignalConfig`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (19 total, 9 thin omitted)

### Community 0 - "QLearningAgent"
Cohesion: 0.10
Nodes (15): DurationQLearningAgent, train_duration_episode(), observe(), QLearningAgent, train_episode(), worker(), EpisodeResult, evaluate() (+7 more)

### Community 1 - "traffic_history.py"
Cohesion: 0.18
Nodes (12): get_traffic_history(), _connect(), _db_path(), _features(), _fit(), forecast_site(), history_summary(), _metrics() (+4 more)

### Community 2 - "Product, Pages, and Premium UI Direction"
Cohesion: 0.18
Nodes (10): About page, Accessibility, Compare page, Information architecture, Interaction and states, Learn page, Product, Pages, and Premium UI Direction, Simulate page (primary) (+2 more)

### Community 4 - "Milestones and Acceptance Checks"
Cohesion: 0.04
Nodes (40): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria (+32 more)

### Community 5 - "collect_traffic_history.py"
Cohesion: 0.19
Nodes (6): collect_traffic_history(), fetch_live_intersections(), fetch_site_observations(), _number(), save_snapshot(), main()

### Community 6 - "routes.py"
Cohesion: 0.10
Nodes (19): control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), get_traffic_forecast(), health(), live_traffic() (+11 more)

### Community 8 - "Decisions and Progress Log"
Cohesion: 0.07
Nodes (28): 2026-11-08 — Background training progress, 2026-11-08 — Browser check of trained comparison, 2026-11-08 — Comparison reporting and CSV export, 2026-11-08 — Configurable paired-seed evaluation, 2026-11-08 — Configurable training and policy guide, 2026-11-08 — Duration policy in live simulation, 2026-11-08 — Full evaluation report CSV, 2026-11-08 — Green-duration semi-Markov agent (+20 more)

### Community 10 - "Backend"
Cohesion: 0.29
Nodes (5): Backend, Endpoints, Install and run, Optional checks, Signal Lab frontend

### Community 17 - "app.js"
Cohesion: 0.20
Nodes (23): captureTrafficSnapshot(), createRun(), doStep(), downloadReport(), drawCars(), drawForecastChart(), drawHistory(), exportEpisodes() (+15 more)

### Community 21 - "TrafficEnvironment"
Cohesion: 0.13
Nodes (10): FixedTimeController, run_episode(), Approach, Metrics, Phase, Scenario, SignalConfig, Snapshot (+2 more)

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `QLearningAgent`, `routes.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `QLearningAgent` be split into smaller, more focused modules?**
  _Cohesion score 0.10014513788098693 - nodes in this community are weakly interconnected._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Milestones and Acceptance Checks` be split into smaller, more focused modules?**
  _Cohesion score 0.044444444444444446 - nodes in this community are weakly interconnected._
- **Are the 6 inferred relationships involving `train_episode()` (e.g. with `.act()` and `.end_episode()`) actually correct?**
  _`train_episode()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09747899159663866 - nodes in this community are weakly interconnected._