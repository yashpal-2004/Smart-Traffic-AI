# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 16 files · ~3,524 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 127 nodes · 228 edges · 14 communities (10 shown, 4 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6161fe77`
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

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 29 edges
2. `QLearningAgent` - 15 edges
3. `train_episode()` - 13 edges
4. `SignalConfig` - 13 edges
5. `SimulatorTests` - 12 edges
6. `FixedTimeController` - 10 edges
7. `Milestones and Acceptance Checks` - 9 edges
8. `Phase` - 9 edges
9. `Scenario` - 9 edges
10. `observe()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `SimulatorTests` --uses--> `Approach`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `Phase`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `Phase`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `Scenario`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (14 total, 4 thin omitted)

### Community 0 - "environment.py"
Cohesion: 0.15
Nodes (5): Approach, Metrics, Phase, Scenario, SignalConfig

### Community 1 - "TrafficEnvironment"
Cohesion: 0.22
Nodes (4): FixedTimeController, Snapshot, TrafficEnvironment, SimulatorTests

### Community 2 - "Product, Pages, and Premium UI Direction"
Cohesion: 0.18
Nodes (10): About page, Accessibility, Compare page, Information architecture, Interaction and states, Learn page, Product, Pages, and Premium UI Direction, Simulate page (primary) (+2 more)

### Community 3 - "Milestones and Acceptance Checks"
Cohesion: 0.20
Nodes (9): M0 — Documentation and decisions (DONE), M1 — Deterministic simulator core (DONE), M2 — Q-learning agent (NOT STARTED), M3 — Evaluation and evidence (NOT STARTED), M4 — Backend API (NOT STARTED), M5 — Premium frontend (NOT STARTED), M6 — Polish and release (NOT STARTED), Milestones and Acceptance Checks (+1 more)

### Community 4 - "Project Brief"
Cohesion: 0.22
Nodes (8): Core experience, Key assumptions to revisit, Out of scope, Problem and audience, Product, Project Brief, Scope for v1, Success criteria

### Community 5 - "Technical Architecture"
Cohesion: 0.22
Nodes (8): API sketch, Component boundaries, Data and reproducibility, Engineering constraints, Proposed stack, Simulator contract, Suggested repo layout, Technical Architecture

### Community 6 - "QLearningAgent"
Cohesion: 0.20
Nodes (4): observe(), QLearningAgent, train_episode(), QLearningTests

### Community 7 - "AI Agent Handoff Instructions"
Cohesion: 0.40
Nodes (4): AI Agent Handoff Instructions, Handoff note template, Rules, YYYY-MM-DD — Milestone / task

### Community 8 - "Decisions and Progress Log"
Cohesion: 0.33
Nodes (5): 2026-11-08 — M1 deterministic simulator complete, 2026-11-08 — Planning files created, Decisions, Decisions and Progress Log, Progress

### Community 9 - "Smart Traffic AI"
Cohesion: 0.50
Nodes (3): Current status, Smart Traffic AI, Start here

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `environment.py`, `QLearningAgent`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `environment.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1476923076923077 - nodes in this community are weakly interconnected._
- **Why does `QLearningAgent` connect `QLearningAgent` to `environment.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `train_episode()` (e.g. with `.act()` and `.end_episode()`) actually correct?**
  _`train_episode()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Why does `train_episode()` connect `QLearningAgent` to `environment.py`, `TrafficEnvironment`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._