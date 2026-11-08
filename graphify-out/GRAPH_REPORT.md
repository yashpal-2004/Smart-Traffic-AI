# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 34 files · ~16,716 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: .xml 3, (none) 1, .sumocfg 1)

## Summary
- 288 nodes · 711 edges · 16 communities (8 shown, 8 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 56 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8f3c6bbe`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QLearningAgent
- traffic_history.py
- run_sumo_evaluation.py
- Milestones and Acceptance Checks
- ApiTests
- routes.py
- Backend
- app.js
- TrafficEnvironment

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 42 edges
2. `SignalConfig` - 32 edges
3. `QLearningAgent` - 30 edges
4. `train_episode()` - 21 edges
5. `evaluate()` - 17 edges
6. `FixedTimeController` - 16 edges
7. `DurationQLearningAgent` - 15 edges
8. `train_duration_episode()` - 15 edges
9. `Scenario` - 14 edges
10. `run_episode()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Sample evaluation exports` --references--> `episode()`  [INFERRED]
  docs/sample-evaluation/README.md → backend/scripts/run_sumo_evaluation.py
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `SignalConfig`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (16 total, 8 thin omitted)

### Community 0 - "QLearningAgent"
Cohesion: 0.12
Nodes (14): DurationQLearningAgent, train_duration_episode(), observe(), QLearningAgent, train_episode(), worker(), evaluate(), write_report() (+6 more)

### Community 1 - "traffic_history.py"
Cohesion: 0.19
Nodes (12): get_traffic_history(), _connect(), _db_path(), _features(), _fit(), forecast_site(), history_summary(), _metrics() (+4 more)

### Community 2 - "run_sumo_evaluation.py"
Cohesion: 0.12
Nodes (9): EpisodeResult, paired_delta_summary(), summarize(), _binary(), prepare_network(), SumoEnvironment, episode(), main() (+1 more)

### Community 4 - "Milestones and Acceptance Checks"
Cohesion: 0.05
Nodes (38): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria (+30 more)

### Community 6 - "routes.py"
Cohesion: 0.07
Nodes (25): collect_traffic_history(), control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), get_traffic_forecast(), health() (+17 more)

### Community 10 - "Backend"
Cohesion: 0.29
Nodes (5): Backend, Endpoints, Install and run, Optional checks, Signal Lab frontend

### Community 17 - "app.js"
Cohesion: 0.18
Nodes (25): captureTrafficSnapshot(), createRun(), doStep(), downloadReport(), drawCars(), drawForecastChart(), drawHistory(), exportEpisodes() (+17 more)

### Community 21 - "TrafficEnvironment"
Cohesion: 0.13
Nodes (8): FixedTimeController, run_episode(), Approach, Metrics, Phase, Scenario, Snapshot, SimulatorTests

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `QLearningAgent` to `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `QLearningAgent` be split into smaller, more focused modules?**
  _Cohesion score 0.12264150943396226 - nodes in this community are weakly interconnected._
- **Why does `SignalConfig` connect `QLearningAgent` to `run_sumo_evaluation.py`, `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `run_sumo_evaluation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12258064516129032 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `run_sumo_evaluation.py`, `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._