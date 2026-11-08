# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 34 files · ~17,684 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: .xml 3, (none) 1, .sumocfg 1)

## Summary
- 297 nodes · 748 edges · 15 communities (8 shown, 7 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 59 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `630105ed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QLearningAgent
- SumoEnvironment
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
7. `SumoEnvironment` - 15 edges
8. `DurationQLearningAgent` - 15 edges
9. `train_duration_episode()` - 15 edges
10. `Scenario` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Sample evaluation exports` --references--> `episode()`  [INFERRED]
  docs/sample-evaluation/README.md → backend/scripts/run_sumo_evaluation.py
- `create_run()` --uses--> `SumoEnvironment`  [INFERRED]
  backend/app/api/routes.py → backend/app/simulator/sumo/environment.py
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `SignalConfig`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `live_traffic()` --calls--> `fetch_live_intersections()`  [EXTRACTED]
  backend/app/api/routes.py → backend/app/traffic_feed.py

## Import Cycles
- None detected.

## Communities (15 total, 7 thin omitted)

### Community 0 - "QLearningAgent"
Cohesion: 0.10
Nodes (18): DurationQLearningAgent, train_duration_episode(), observe(), QLearningAgent, train_episode(), load_sumo_agent(), worker(), EpisodeResult (+10 more)

### Community 2 - "SumoEnvironment"
Cohesion: 0.14
Nodes (8): delete_run(), simulators(), _binary(), prepare_network(), sumo_gui_status(), SumoEnvironment, episode(), Sample evaluation exports

### Community 4 - "Milestones and Acceptance Checks"
Cohesion: 0.05
Nodes (38): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria (+30 more)

### Community 5 - "collect_traffic_history.py"
Cohesion: 0.10
Nodes (5): fetch_live_intersections(), fetch_site_observations(), _number(), main(), ApiTests

### Community 6 - "routes.py"
Cohesion: 0.07
Nodes (33): collect_traffic_history(), control_run(), create_run(), CreateRunRequest, EvaluationRequest, get_run(), get_traffic_forecast(), get_traffic_history() (+25 more)

### Community 10 - "Backend"
Cohesion: 0.29
Nodes (5): Backend, Endpoints, Install and run, Optional checks, Signal Lab frontend

### Community 17 - "app.js"
Cohesion: 0.15
Nodes (29): captureTrafficSnapshot(), createRun(), doStep(), downloadReport(), drawCars(), drawForecastChart(), drawHistory(), exportEpisodes() (+21 more)

### Community 21 - "TrafficEnvironment"
Cohesion: 0.15
Nodes (9): FixedTimeController, run_episode(), Approach, Metrics, Phase, Scenario, Snapshot, TrafficEnvironment (+1 more)

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `QLearningAgent`, `routes.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `QLearningAgent` be split into smaller, more focused modules?**
  _Cohesion score 0.10451977401129943 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `SumoEnvironment` be split into smaller, more focused modules?**
  _Cohesion score 0.14245014245014245 - nodes in this community are weakly interconnected._
- **Why does `SignalConfig` connect `QLearningAgent` to `SumoEnvironment`, `TrafficEnvironment`, `routes.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._