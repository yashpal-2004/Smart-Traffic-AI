# Project Brief

## Product
A polished, interactive learning lab for adaptive traffic signal control. Users configure traffic demand, run a simulation, watch a signal policy operate, and compare it to a fixed-time controller.

## Problem and audience
Students and early-career ML engineers need an understandable way to see how reinforcement learning decisions affect a system over time. The product should make the state, action, reward, and trade-offs visible rather than presenting an opaque “AI optimized” claim.

## Core experience
1. Choose a scenario (balanced, rush hour, one-road surge) or configure arrival rates.
2. Start, pause, step, or reset a four-way intersection simulation.
3. Observe queues, signal phase, throughput, waiting time, and the agent's current decision.
4. Compare RL with fixed-time control using identical seeded traffic arrivals.
5. Inspect a run summary and learning/evaluation charts.

## Scope for v1
- One four-way, single-lane-per-approach intersection; discrete time and simplified vehicle movement.
- Python simulator and tabular Q-learning first; fixed-time baseline.
- Browser UI with a clear animated intersection and useful charts.
- Reproducible seeded evaluation and honest metric reporting.
- Local-first; no accounts, cloud dependency, real traffic control, or claims of deployment readiness.

## Out of scope
Real-world signal operation, multi-intersection coordination, computer vision, live feeds, advanced vehicle physics, and guaranteeing an optimal policy.

## Success criteria
- User can run, pause, step, and reset a simulation without losing the selected settings.
- Same seed and settings reproduce the same arrival sequence and comparable results.
- RL and baseline are evaluated on the same scenarios and random seeds.
- Dashboard reports mean wait, max queue, throughput, and episode duration with definitions.
- UI explains state/action/reward in plain language and labels training results separately from evaluation results.
- Project can be resumed by another agent using the handoff and progress files.

## Key assumptions to revisit
A custom discrete simulator is preferred for approachable learning and deterministic browser demos. SUMO may be added only after the core experience works and its setup value is justified.
