# Decisions and Progress Log

## Decisions
- **2026-11-08:** Start with a custom discrete single-intersection simulator; it is easier to understand and reproduce than adopting a large traffic simulator before the core idea is proven.
- **2026-11-08:** Begin with fixed-time baseline plus tabular Q-learning. Keep RL explicitly educational; compare on matched seeds.
- **2026-11-08:** Proposed web stack is FastAPI + React/TypeScript/Vite. Confirm workspace/repository placement before implementation.
- **2026-11-08:** No real-world traffic control or claims of deployment readiness.

## Progress
### 2026-11-08 — Planning files created
- Status: M0 documentation created; implementation not started.
- Files: project brief, UI plan, architecture, milestones, agent handoff, this log.
- Verification: checked target workspace existed before creating project folder.
- Next exact step: inspect the new folder and decide whether implementation should begin in this folder or another existing repository; then start M1.


### 2026-11-08 — M1 deterministic simulator complete
- Status: DONE.
- Changed: added the seeded four-approach environment, three demand scenarios, configurable green/amber timing, queue and wait metrics, fixed-time policy, and five deterministic acceptance tests.
- Decisions: arrivals are Bernoulli per approach per simulated second; active opposing approaches each serve at most one vehicle per second; amber ticks block service; vehicle wait is measured from arrival through service.
- Verification: `PYTHONPATH=backend python3 -m unittest discover -s backend/tests -v` — 5 tests passed. `graphify update .` completed.
- Known limitations: simplified one-lane intersection and per-second Bernoulli traffic; no UI/API yet.
- Next exact step: implement tabular Q-learning with discrete queue/phase observations, legal hold/switch actions, training loop, and deterministic checkpointing (M2).
