# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 34 files · ~17,271 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: .xml 3, (none) 1, .sumocfg 1)

## Summary
- 296 nodes · 742 edges · 17 communities (10 shown, 7 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b6532485`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QLearningAgent
- traffic_history.py
- SumoEnvironment
- runner.py
- Milestones and Acceptance Checks
- collect_traffic_history.py
- routes.py
- Backend
- app.js
- TrafficEnvironment

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 42 edges
2. `SignalConfig` - 32 edges
3. `QLearningAgent` - 31 edges
4. `train_episode()` - 21 edges
5. `evaluate()` - 17 edges
6. `FixedTimeController` - 16 edges
7. `DurationQLearningAgent` - 15 edges
8. `SumoEnvironment` - 15 edges
9. `train_duration_episode()` - 15 edges
10. `Scenario` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Sample evaluation exports` --references--> `episode()`  [INFERRED]
  docs/sample-evaluation/README.md → backend/scripts/run_sumo_evaluation.py
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `SignalConfig`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `Phase`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `Approach`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (17 total, 7 thin omitted)

### Community 0 - "QLearningAgent"
Cohesion: 0.11
Nodes (17): DurationQLearningAgent, train_duration_episode(), observe(), QLearningAgent, train_episode(), worker(), EpisodeResult, evaluate() (+9 more)

### Community 1 - "traffic_history.py"
Cohesion: 0.19
Nodes (12): get_traffic_history(), _connect(), _db_path(), _features(), _fit(), forecast_site(), history_summary(), _metrics() (+4 more)

### Community 2 - "SumoEnvironment"
Cohesion: 0.26
Nodes (4): delete_run(), SumoEnvironment, episode(), Sample evaluation exports

### Community 3 - "runner.py"
Cohesion: 0.21
Nodes (3): Approach, Phase, prepare_network()

### Community 4 - "Milestones and Acceptance Checks"
Cohesion: 0.05
Nodes (38): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria (+30 more)

### Community 5 - "collect_traffic_history.py"
Cohesion: 0.11
Nodes (7): collect_traffic_history(), fetch_live_intersections(), fetch_site_observations(), _number(), save_snapshot(), main(), ApiTests

### Community 6 - "routes.py"
Cohesion: 0.09
Nodes (22): control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), get_traffic_forecast(), health(), live_traffic() (+14 more)

### Community 10 - "Backend"
Cohesion: 0.29
Nodes (5): Backend, Endpoints, Install and run, Optional checks, Signal Lab frontend

### Community 17 - "app.js"
Cohesion: 0.15
Nodes (29): captureTrafficSnapshot(), createRun(), doStep(), downloadReport(), drawCars(), drawForecastChart(), drawHistory(), exportEpisodes() (+21 more)

### Community 21 - "TrafficEnvironment"
Cohesion: 0.16
Nodes (7): FixedTimeController, run_episode(), Metrics, Scenario, Snapshot, TrafficEnvironment, SimulatorTests

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `QLearningAgent`, `runner.py`, `routes.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `QLearningAgent` be split into smaller, more focused modules?**
  _Cohesion score 0.11103896103896103 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Milestones and Acceptance Checks` be split into smaller, more focused modules?**
  _Cohesion score 0.047619047619047616 - nodes in this community are weakly interconnected._
- **Why does `SignalConfig` connect `QLearningAgent` to `SumoEnvironment`, `runner.py`, `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._