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


### 2026-11-08 — M2 Q-learning core implemented
- Status: Implementation complete; M2 acceptance review in progress.
- Changed: added bounded queue/phase observation, legal hold/switch actions, tabular Q-learning, epsilon-greedy exploration, fixed-length episode trainer, metrics output, and versioned JSON checkpoint save/load.
- Decisions: state has capped queue buckets (0–5), phase id, and green-age bucket; reward is vehicles served this tick minus 0.1 times the remaining queued vehicles; min-green prevents early switches and max-green forces a switch.
- Verification: `PYTHONPATH=backend python3 -m unittest discover -s backend/tests -v` — 9 tests passed; fixed-seed training and checkpoint round trip verified. `graphify update .` completed.
- Known limitations: tabular state is intentionally small and can generalize poorly; evaluation runner and learned-vs-baseline results are still needed.
- Next exact step: add reproducible episode evaluation and report fixed-time vs trained Q-learning on matched seeds and all three demand scenarios (M3).


### 2026-11-08 — M3 evaluation runner implemented
- Status: evaluation pipeline implemented; performance interpretation and tuning remain in progress.
- Changed: added paired-seed scenario evaluation, mean/median/population spread summaries, JSON report output, and a train/evaluate CLI script with separate training and held-out evaluation seeds.
- Verification: all 11 tests passed. End-to-end command `PYTHONPATH=backend python3 backend/scripts/train_and_evaluate.py --episodes 100 --steps 200 --output /tmp/traffic-evaluation.json` completed.
- Observed result for this smoke experiment only: across 3 scenarios × 5 held-out seeds (15 episodes/controller), fixed-time mean served wait was 22.58s, mean queue 44.74 and mean served 248.5; Q-learning was 24.75s, 54.66 and 225.3. This trained policy did worse; do not claim improvement.
- Known limitations: 100 episodes × 200 steps is a smoke run, not robust model selection; demand rates may exceed the single-lane service capacity, making queues grow.
- Next exact step: inspect reward and demand/service design, then run longer training and report whether policy improves against fixed-time before building the API/UI.
