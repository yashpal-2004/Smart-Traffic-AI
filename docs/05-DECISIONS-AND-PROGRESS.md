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


### 2026-11-08 — Background training progress
- Status: implemented; pending live-browser check.
- Changed: model training now runs in a worker thread with `/api/training` progress/status polling; the UI displays episode progress and completion/failure state while remaining responsive. Newly trained policies are attached to active runs and used for later evaluations.
- Verification: all 16 backend tests pass, including queue history and background training completion polling.
- Known limitations: training jobs and progress are process-local and not resumable after server restart; API evaluation still runs synchronously.
- Next exact step: verify the browser progress display, then improve comparison interpretation/export and revisit model quality.


### 2026-11-08 — Comparison reporting and CSV export
- Status: implemented; browser verification pending.
- Changed: evaluation responses identify whether a trained policy was used and its Q-table state count; Compare page shows model status, side-by-side metric bars, trained/untrained interpretation, and downloadable episode-level CSV.
- Verification: all 16 backend tests pass, including trained-policy metadata in evaluation responses.
- Known limitations: the visualization scales each metric independently and CSV export is client-side; no confidence intervals or paired significance tests are presented.
- Next exact step: verify the comparison display in browser and continue improving experimental rigor (paired deltas and clearer queue/wait definitions).


### 2026-11-08 — Browser check of trained comparison
- Verification: reloaded dashboard, confirmed API online and model status at 38 states; ran default matched comparison (3 scenarios × 3 seeds, 500 steps). Fixed-time mean served wait 11.77s, mean queue 13.41, served 545.8; Q-learning 14.24s, 16.39, served 543.0.
- Interpretation: on this small run, the trained policy still underperforms; the UI reports results without claiming a gain. Episode CSV export control is visible.


### 2026-11-08 — Q-learning reward/state experiment
- Status: experiment rejected; no performance improvement.
- Changed: increased green-age resolution to five-second buckets, slowed epsilon decay, added randomized tie-breaking, and changed reward to accumulated queue delay with a small throughput term.
- Verification: existing 16 backend checks still pass in the preceding run before this experiment; training/evaluation CLI completed at 1,500 and 5,000 episodes, 500 steps, with 15 held-out episodes per controller.
- Results: fixed-time remained at 11.29s served wait, 12.71 mean queue, 535.4 served. Revised Q-learning at 1,500 episodes: 13.53s, 16.31, 527.9. At 5,000 episodes: 21.17s, 24.23, 512.5. More training worsened this policy.
- Conclusion: the tabular Q-learning formulation is not useful yet. Do not use its checkpoint as evidence of an improved controller. The project needs a better action/state/reward formulation (or a clearly labelled adaptive heuristic comparator) before presenting RL effectiveness.
- Next exact step: design a green-duration action space and measure the transition reward/credit assignment with a small controlled sweep, keeping fixed-time as the baseline.


### 2026-11-08 — Green-duration semi-Markov agent
- Status: implemented and wired into local evaluation.
- Changed: added a separate tabular duration-based Q-learning agent with actions selecting 10/15/20/25/30 second greens; each decision learns from accumulated reward across the green interval and amber transition. Added a controlled comparison script. The training API now trains/saves both hold-switch and duration policies; evaluation includes the duration policy when present; model status reports both state counts.
- Verification: all 17 backend tests pass, including duration action legality, fixed-length episode completion, table shape, API training completion and evaluation.
- Controlled experiment: 1,500 episodes × 500 steps; held-out 5 seeds across 3 scenarios (15 episodes each). Fixed-time mean wait 11.10s, queue 12.80, served 544.6; hold/switch Q-learning 15.31s, 19.26, 531.1; duration Q-learning 12.34s, 14.99, 538.9. Duration policy improved over hold/switch but remains behind fixed-time.
- Next exact step: refresh browser and confirm three-policy report, then add the duration policy to the live simulation controller options and improve reward/state tuning without claiming a win.
- Browser verification: three-policy report is live; default quick evaluation showed duration policy at 16.11s wait and 19.35 queue, between hold/switch (17.74s, 23.16) and fixed-time (11.77s, 13.41). The quick UI evaluation uses a small locally saved model and 9 episodes; the controlled script result above is the more relevant comparison.


### 2026-11-08 — Duration policy in live simulation
- Status: implemented.
- Changed: added green-duration Q-learning to the run controller choices; each green phase chooses a target duration and then switches through the configured amber period; API snapshots expose the current target; UI identifies the policy and displays its chosen target. The option returns a clear conflict response before a duration model has been trained.
- Verification: 18 backend checks pass, including training then starting/stepping a duration-policy run. Browser check confirms controller selector entry, live step, and target display (30s in observed step).
- Next exact step: expose duration action/reward traces in the Learn page and provide longer, selectable training settings before more controlled policy tuning.


### 2026-11-08 — Configurable training and policy guide
- Status: implemented and browser-verified.
- Changed: Compare now accepts a selectable episode count and steps per episode, trains both Q-learning variants, and reports live learned-state counts for each. The Learn page explains the duration action set and interval-based reward; comparison copy names all three policies.
- Verification: all 18 backend tests pass. Browser check confirmed both numeric controls, the training button, and duration/reward explanations.
- Known limitation: the two tabular agents are still trained sequentially in one process-local background job; training progress is not resumable after a server restart.
- Next exact step: add evaluation controls for seed count and make matched per-seed deltas easier to inspect before further policy tuning.


### 2026-11-08 — Configurable paired-seed evaluation
- Status: implemented and browser-verified.
- Changed: Compare accepts 1–30 matched seeds, generates a reproducible seed sequence, and displays per-scenario/per-seed wait, queue, and served-count deltas for each learned policy against fixed-time. Negative wait/queue deltas mean lower values than baseline.
- Verification: local dashboard completed an evaluation with two seeds, three scenarios, and 100 steps; all 12 paired delta rows rendered with policy names and baseline definitions.
- Known limitation: this is descriptive paired reporting; it does not calculate confidence intervals or statistical significance.
- Next exact step: inspect the interval behavior across larger seed counts, document sample-size sensitivity, and add scenario-specific paired summaries.


### 2026-11-08 — Paired improvement summary and uncertainty intervals
- Status: implemented; browser verification pending.
- Changed: evaluation responses summarize wait, queue, and served-count paired differences with two-sided 95% t intervals, plus the count of episodes where wait improved or tied. The Compare page presents interval estimates and win counts above the row-level table.
- Method: intervals use the sample standard deviation of paired differences and a t critical value through 30 observations, then 1.96 for larger samples. Values are rounded to three decimals.
- Known limitation: pooled intervals combine scenarios and assume independent paired differences with an approximately normal mean; small seed counts produce wide, unstable intervals and should be interpreted cautiously.
- Next exact step: inspect interval behavior across larger seed counts, document sample-size sensitivity, and add scenario-specific paired summaries.


### 2026-11-08 — Scenario-specific paired summaries
- Status: implemented and browser-verified.
- Changed: evaluation now reports paired mean differences and wait-improvement counts separately for each selected traffic scenario, in addition to the pooled summary. The dashboard labels each scenario group and shows its seed sample count in the win-count denominator.
- Accuracy fix: confidence intervals are unavailable when a group has only one paired sample; the UI labels that case instead of presenting a zero-width interval.
- Verification: a live 2-seed, 3-scenario evaluation rendered all three scenario groups, six policy cards, and 12 per-seed delta rows. The two-seed t intervals are visibly wide, as expected.
- Known limitation: scenario-level intervals can be unstable at low seed counts; the pooled interval still combines scenarios and is shown separately.
- Next exact step: export the paired summaries and interval method with the episode CSV, and add a clearer experiment protocol section.


### 2026-11-08 — Full evaluation report CSV
- Status: implemented; UI action verified.
- Changed: CSV export now uses typed record rows for protocol/method, controller summaries, pooled and scenario-specific paired intervals, individual paired deltas, and complete episode JSON. Export button now describes the full report.
- Format: one consistent column schema across record types; each row identifies its type and relevant scenario, seed, controller, and metric. Blob URL cleanup is delayed briefly to allow the browser to start the download.
- Verification: live single-seed evaluation showed the correct unavailable-interval message and scenario cards; clicked the full-report export action.
- Known limitation: browser download storage was not exposed for direct file inspection; episode details are embedded as JSON in a CSV cell.
- Next exact step: verify downloaded file has every record type and valid CSV escaping, then add a JSON download option for direct machine ingestion.


### 2026-11-08 — JSON report download and report identity
- Status: implemented and browser-verified.
- Changed: evaluation responses now include a unique report ID and UTC generation timestamp. Compare offers a structured JSON download alongside the full-report CSV; both filenames include the report ID, and CSV protocol rows include report metadata.
- Verification: a live single-seed report displayed its ID and generation timestamp, showed both download controls, and triggered each export action. The one-sample interval message remained correct.
- Known limitation: browser download storage was not exposed for file-content inspection; report IDs are generated per API response and are not persisted by the server.
- Next exact step: add route/config and model checkpoint identifiers to the exported report so results retain more context for reproduction.
