# Graph Report - Smart-Traffic-AI  (2026-11-08)

## Corpus Check
- 14 files · ~2,842 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 99 nodes · 151 edges · 14 communities (8 shown, 6 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `287ad7a4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- environment.py
- TrafficEnvironment
- Product, Pages, and Premium UI Direction
- Milestones and Acceptance Checks
- Project Brief
- Technical Architecture
- FixedTimeController
- AI Agent Handoff Instructions
- Decisions and Progress Log
- Smart Traffic AI
- backend/README.md

## God Nodes (most connected - your core abstractions)
1. `TrafficEnvironment` - 20 edges
2. `SimulatorTests` - 12 edges
3. `SignalConfig` - 11 edges
4. `FixedTimeController` - 10 edges
5. `Scenario` - 9 edges
6. `Milestones and Acceptance Checks` - 9 edges
7. `Phase` - 8 edges
8. `Project Brief` - 8 edges
9. `Technical Architecture` - 8 edges
10. `Product, Pages, and Premium UI Direction` - 6 edges

## Surprising Connections (you probably didn't know these)
- `FixedTimeController` --uses--> `Phase`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `SignalConfig`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `FixedTimeController` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/app/agents/fixed_time.py → backend/app/simulator/environment.py
- `SimulatorTests` --uses--> `FixedTimeController`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/agents/fixed_time.py
- `SimulatorTests` --uses--> `TrafficEnvironment`  [INFERRED]
  backend/tests/test_simulator.py → backend/app/simulator/environment.py

## Import Cycles
- None detected.

## Communities (14 total, 6 thin omitted)

### Community 0 - "environment.py"
Cohesion: 0.17
Nodes (6): Approach, Metrics, Phase, Scenario, SignalConfig, SimulatorTests

### Community 2 - "Product, Pages, and Premium UI Direction"
Cohesion: 0.18
Nodes (10): About page, Accessibility, Compare page, Information architecture, Interaction and states, Learn page, Product, Pages, and Premium UI Direction, Simulate page (primary) (+2 more)

### Community 3 - "Milestones and Acceptance Checks"
Cohesion: 0.20
Nodes (9): M0 — Documentation and decisions (DONE), M1 — Deterministic simulator core (IN PROGRESS), M2 — Q-learning agent (NOT STARTED), M3 — Evaluation and evidence (NOT STARTED), M4 — Backend API (NOT STARTED), M5 — Premium frontend (NOT STARTED), M6 — Polish and release (NOT STARTED), Milestones and Acceptance Checks (+1 more)

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
Cohesion: 0.40
Nodes (4): 2026-11-08 — Planning files created, Decisions, Decisions and Progress Log, Progress

### Community 9 - "Smart Traffic AI"
Cohesion: 0.50
Nodes (3): Current status, Smart Traffic AI, Start here

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TrafficEnvironment` connect `TrafficEnvironment` to `environment.py`, `FixedTimeController`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `TrafficEnvironment` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`TrafficEnvironment` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Why does `SignalConfig` connect `environment.py` to `TrafficEnvironment`, `FixedTimeController`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `SimulatorTests` (e.g. with `FixedTimeController` and `Approach`) actually correct?**
  _`SimulatorTests` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Why does `FixedTimeController` connect `FixedTimeController` to `environment.py`, `TrafficEnvironment`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SignalConfig` (e.g. with `FixedTimeController` and `SimulatorTests`) actually correct?**
  _`SignalConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `FixedTimeController` (e.g. with `Phase` and `SignalConfig`) actually correct?**
  _`FixedTimeController` has 4 INFERRED edges - model-reasoned connections that need verification._