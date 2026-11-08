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


### 2026-11-08 — M3 demand review, M4 API, M5 visual dashboard
- Status: API and initial visual interface implemented; M3 model quality remains in progress; M5 polish/accessibility acceptance still needs review.
- Changed: added FastAPI routes for scenarios, run lifecycle, stepping and evaluation; added CORS for local UI; added a responsive dark control-room dashboard with live intersection, metrics, controller selection, comparison and learn pages.
- Demand decision: rates are below nominal single-lane per-approach service capacity to make queues stable enough for controller comparison (balanced .20, rush .40, north surge [.45,.15,.20,.15]).
- Verification: 15 backend tests pass; frontend connected to API in browser, and run control advanced sim clock. End-to-end 1,000-episode × 500-step train/evaluation gave fixed-time mean wait 11.29s, queue 12.71, served 535.4; Q-learning mean wait 17.37s, queue 21.59, served 513.0 over 15 held-out episodes per controller. Learned policy still underperforms; results are not presented as an improvement.
- Local run: `pip install -r backend/requirements.txt && PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload`; separate terminal `python3 -m http.server 4173 --bind 127.0.0.1 --directory frontend`.
- Known limitations: Q-learning control is not competitive yet; UI comparison uses an untrained in-memory table unless a checkpoint path is later wired; runs are process-local; UI uses inline SVG and basic summaries rather than time-series charts.
- Next exact step: investigate Q-learning reward/state/action behavior and load trained checkpoint for comparison; then add chart history and finish M3/M5 acceptance review.


### 2026-11-08 — Trainable model and live history
- Status: implemented and ready for continued evaluation.
- Changed: added an on-demand training API that saves a versioned Q-table locally; simulation runs and matched evaluations now use the loaded trained model; run snapshots include bounded queue/wait/served history; dashboard includes a queue/wait SVG history chart and Train Q-learning control.
- Verification: 16 backend tests pass, including run history and a short training request; dashboard reload confirmed API online and Compare page shows training control.
- Known limitations: UI training currently runs synchronously and can take a while at default 500 × 500; trained model persists on local disk only; current tabular policy quality still requires serious evaluation.
- Next exact step: benchmark trained policy with longer fixed-seed training and held-out seeds, add training progress feedback or background job if needed, and improve chart axis/legend semantics.
