# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 33 files · ~15,368 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: .xml 3, (none) 1, .sumocfg 1)

## Summary
- 287 nodes · 709 edges · 17 communities (8 shown, 9 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 55 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7eb24c0f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QLearningAgent
- traffic_history.py
- run_sumo_evaluation.py
- sample-evaluation/README.md
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
10. `main()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `SignalConfig`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `episode()` --calls--> `FixedTimeController`  [EXTRACTED]
  backend/scripts/run_sumo_evaluation.py → backend/app/agents/fixed_time.py

## Import Cycles
- None detected.

## Communities (17 total, 9 thin omitted)

### Community 0 - "QLearningAgent"
Cohesion: 0.12
Nodes (14): DurationQLearningAgent, train_duration_episode(), observe(), QLearningAgent, train_episode(), worker(), evaluate(), write_report() (+6 more)

### Community 1 - "traffic_history.py"
Cohesion: 0.19
Nodes (12): get_traffic_history(), _connect(), _db_path(), _features(), _fit(), forecast_site(), history_summary(), _metrics() (+4 more)

### Community 2 - "run_sumo_evaluation.py"
Cohesion: 0.14
Nodes (8): EpisodeResult, paired_delta_summary(), summarize(), _binary(), prepare_network(), SumoEnvironment, episode(), main()

### Community 4 - "Milestones and Acceptance Checks"
Cohesion: 0.05
Nodes (37): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria (+29 more)

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
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `QLearningAgent` to `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `QLearningAgent` be split into smaller, more focused modules?**
  _Cohesion score 0.12264150943396226 - nodes in this community are weakly interconnected._
- **Why does `SignalConfig` connect `QLearningAgent` to `run_sumo_evaluation.py`, `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `run_sumo_evaluation.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1354679802955665 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `run_sumo_evaluation.py`, `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._