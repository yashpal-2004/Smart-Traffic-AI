# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 21 files · ~15,047 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 149 nodes · 306 edges · 18 communities (11 shown, 7 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `025a6fc4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- environment.py
- TrafficEnvironment
- Product, Pages, and Premium UI Direction
- Milestones and Acceptance Checks
- Project Brief
- Technical Architecture
- QLearningAgent
- AI Agent Handoff Instructions
- Decisions and Progress Log
- Smart Traffic AI
- backend/README.md
- QLearningAgent
- runner.py

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 33 edges
2. `QLearningAgent` - 24 edges
3. `SignalConfig` - 21 edges
4. `train_episode()` - 15 edges
5. `run_episode()` - 12 edges
6. `Scenario` - 12 edges
7. `FixedTimeController` - 12 edges
8. `SimulatorTests` - 12 edges
9. `evaluate()` - 11 edges
10. `main()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `run_episode()` --uses--> `QLearningAgent`  [INFERRED]
  backend/app/evaluation/runner.py → backend/app/agents/q_learning.py
- `FixedTimeController` --uses--> `Phase`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `SignalConfig`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `FixedTimeController`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/agents/fixed_time.py

## Import Cycles
- None detected.

## Communities (18 total, 7 thin omitted)

### Community 0 - "environment.py"
Cohesion: 0.20
Nodes (5): Approach, Metrics, Phase, Scenario, SimulatorTests

### Community 1 - "TrafficEnvironment"
Cohesion: 0.25
Nodes (4): FixedTimeController, run_episode(), Snapshot, TrafficEnvironment

### Community 2 - "Product, Pages, and Premium UI Direction"
Cohesion: 0.18
Nodes (10): About page, Accessibility, Compare page, Information architecture, Interaction and states, Learn page, Product, Pages, and Premium UI Direction, Simulate page (primary) (+2 more)

### Community 3 - "Milestones and Acceptance Checks"
Cohesion: 0.20
Nodes (9): M0 — Documentation and decisions (DONE), M1 — Deterministic simulator core (DONE), M2 — Q-learning agent (IN PROGRESS), M3 — Evaluation and evidence (IN PROGRESS), M4 — Backend API (NOT STARTED), M5 — Premium frontend (NOT STARTED), M6 — Polish and release (NOT STARTED), Milestones and Acceptance Checks (+1 more)

### Community 4 - "Project Brief"
Cohesion: 0.22
Nodes (8): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria

### Community 5 - "Technical Architecture"
Cohesion: 0.22
Nodes (8): API sketch, Component boundaries, Data and reproducibility, Engineering constraints, Proposed stack, Simulator contract, Suggested repo layout, Technical Architecture

### Community 7 - "AI Agent Handoff Instructions"
Cohesion: 0.40
Nodes (4): AI Agent Handoff Instructions, Handoff note template, Rules, YYYY-MM-DD — Milestone / task

### Community 8 - "Decisions and Progress Log"
Cohesion: 0.25
Nodes (7): 2026-11-08 — M1 deterministic simulator complete, 2026-11-08 — M2 Q-learning core implemented, 2026-11-08 — M3 evaluation runner implemented, 2026-11-08 — Planning files created, Decisions, Decisions and Progress Log, Progress

### Community 9 - "Smart Traffic AI"
Cohesion: 0.50
Nodes (3): Current status, Smart Traffic AI, Start here

### Community 14 - "QLearningAgent"
Cohesion: 0.21
Nodes (6): QLearningAgent, evaluate(), SignalConfig, main(), EvaluationTests, QLearningTests

### Community 15 - "runner.py"
Cohesion: 0.20
Nodes (3): EpisodeResult, summarize(), write_report()

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `environment.py`, `QLearningAgent`, `QLearningAgent`, `runner.py`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Why does `QLearningAgent` connect `QLearningAgent` to `TrafficEnvironment`, `QLearningAgent`, `runner.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `QLearningAgent` (e.g. with `evaluate()` and `run_episode()`) actually correct?**
  _`QLearningAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Why does `SignalConfig` connect `QLearningAgent` to `environment.py`, `TrafficEnvironment`, `runner.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `train_episode()` (e.g. with `.act()` and `.end_episode()`) actually correct?**
  _`train_episode()` has 6 INFERRED edges - model-reasoned connections that need verification._