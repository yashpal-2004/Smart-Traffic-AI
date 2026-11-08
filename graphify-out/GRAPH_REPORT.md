# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 31 files · ~14,489 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 1, .csv 1, .css 1)

## Summary
- 265 nodes · 624 edges · 16 communities (8 shown, 8 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `85a3f839`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QLearningAgent
- traffic_history.py
- sample-evaluation/README.md
- Milestones and Acceptance Checks
- collect_traffic_history.py
- routes.py
- Backend
- app.js
- TrafficEnvironment

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 42 edges
2. `QLearningAgent` - 28 edges
3. `SignalConfig` - 28 edges
4. `train_episode()` - 19 edges
5. `evaluate()` - 17 edges
6. `DurationQLearningAgent` - 15 edges
7. `train_duration_episode()` - 15 edges
8. `FixedTimeController` - 14 edges
9. `run_episode()` - 13 edges
10. `Scenario` - 12 edges

## Surprising Connections (you probably didn't know these)
- `QLearningTests` --uses--> `DurationQLearningAgent`  [INFERRED]
  backend/tests/test_q_learning.py → backend/app/agents/duration_q_learning.py
- `run_episode()` --references--> `QLearningAgent`  [EXTRACTED]
  backend/app/evaluation/runner.py → backend/app/agents/q_learning.py
- `SimulatorTests` --uses--> `Approach`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `Phase`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `Phase`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (16 total, 8 thin omitted)

### Community 0 - "QLearningAgent"
Cohesion: 0.11
Nodes (12): DurationQLearningAgent, QLearningAgent, train_episode(), worker(), EpisodeResult, evaluate(), paired_delta_summary(), summarize() (+4 more)

### Community 1 - "traffic_history.py"
Cohesion: 0.20
Nodes (10): _connect(), _db_path(), _features(), _fit(), forecast_site(), _metrics(), _parse_time(), _predict() (+2 more)

### Community 4 - "Milestones and Acceptance Checks"
Cohesion: 0.05
Nodes (35): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria (+27 more)

### Community 5 - "collect_traffic_history.py"
Cohesion: 0.09
Nodes (7): live_traffic(), fetch_live_intersections(), fetch_site_observations(), _number(), save_snapshot(), main(), ApiTests

### Community 6 - "routes.py"
Cohesion: 0.09
Nodes (21): collect_traffic_history(), control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), get_traffic_forecast(), get_traffic_history() (+13 more)

### Community 10 - "Backend"
Cohesion: 0.29
Nodes (5): Backend, Endpoints, Install and run, Optional checks, Signal Lab frontend

### Community 17 - "app.js"
Cohesion: 0.18
Nodes (25): captureTrafficSnapshot(), createRun(), doStep(), downloadReport(), drawCars(), drawForecastChart(), drawHistory(), exportEpisodes() (+17 more)

### Community 21 - "TrafficEnvironment"
Cohesion: 0.11
Nodes (13): train_duration_episode(), FixedTimeController, observe(), run_episode(), Approach, Metrics, Phase, Scenario (+5 more)

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `QLearningAgent`, `routes.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `QLearningAgent` be split into smaller, more focused modules?**
  _Cohesion score 0.11304347826086956 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Milestones and Acceptance Checks` be split into smaller, more focused modules?**
  _Cohesion score 0.05128205128205128 - nodes in this community are weakly interconnected._
- **Are the 6 inferred relationships involving `train_episode()` (e.g. with `.act()` and `.end_episode()`) actually correct?**
  _`train_episode()` has 6 INFERRED edges - model-reasoned connections that need verification._