# Milestones and Acceptance Checks

Status key: `NOT STARTED`, `IN PROGRESS`, `BLOCKED`, `DONE`.

## M0 — Documentation and decisions (DONE)
- [x] Product brief, UI plan, architecture, milestones, and handoff guide created.
- [x] Confirm repository layout and implementation stack before coding.

## M1 — Deterministic simulator core (DONE)
- [x] Implement queue/vehicle model, phases, transitions, arrivals, movement, metrics, seeded RNG.
- [x] Add fixed-time baseline.
- [x] Define and test step ordering and edge cases.
**Acceptance:** same seed/config produces identical trace; no vehicle disappears except when served; no conflicting phases; metrics match hand-calculated tiny scenarios.

## M2 — Q-learning agent (DONE)
- [x] Define discrete observation encoding and legal actions.
- [x] Implement Q-table, epsilon-greedy policy, training loop, checkpoint format.
- [x] Log episode reward and core metrics.
**Acceptance:** train/evaluate separation exists; agent can complete episodes without invalid actions; learning curve is reproducible for fixed seeds.

## M3 — Evaluation and evidence (DONE)
- [x] Compare fixed-time and RL on matched seeds and at least three demand patterns.
- [x] Report mean, median, spread, sample count, and definitions.
- [x] Reserve held-out seeds; reward tuning remains future work.
**Acceptance:** results exportable; no cherry-picked single-run claims; README includes limitations and actual measured results.

## M4 — Backend API (DONE)
- [x] Create run/step/control/evaluation endpoints and schema validation.
- [x] Add clear error responses and in-memory run state.
**Acceptance:** API can drive a complete deterministic run and return metrics; API docs reflect actual behavior.

## M5 — Premium frontend (DONE)
- [x] Build responsive Simulate, Compare, Learn pages.
- [x] Add intersection visualization, run controls, metric cards, controller comparison, educational explanations.
- [x] Add empty/error handling, keyboard-operable controls, reduced motion.
**Acceptance:** core workflow usable without reading source; visualization agrees with backend snapshots; no placeholder metrics.

## M6 — Polish and release (DONE)
- [x] Add clean-clone setup docs, a dashboard screenshot, and an architecture diagram.
- [x] Add a sample JSON and CSV evaluation export.
- [x] Review responsive breakpoints and accessibility semantics/focus treatment.
- [x] Finish a clean-clone startup smoke check and record the exact outcome.
**Acceptance:** clean clone setup works; all claims trace to reproducible results; limitations are visible.

## M7 — Public traffic feed integration (DONE)
- [x] Add a read-only adapter for Brisbane City Council's public signal-volume feed.
- [x] Expose current site summaries through the API and display flow, detector occupancy, and feed age in a dedicated dashboard page.
- [x] Show source attribution, license, measurement units, data freshness, and the non-control limitation in the UI and documentation.
- [x] Confirm the dashboard loads from a clean page session and close the milestone.
**Acceptance:** live public measurements can be read and explored; missing/upstream errors are visible; the app never sends commands to external signals or presents lane identifiers as directions.

## M8 — Traffic forecasting portfolio workflow (DONE)
- [x] Persist unique public traffic observations locally with a repeatable collector and API capture path.
- [x] Implement an interpretable lag-based ridge model and persistence baseline.
- [x] Evaluate with a chronological one-step holdout and MAE/RMSE; expose observations and predictions in the dashboard.
- [x] Collect at least 24 distinct observations for a site and record the real-data model-versus-baseline metrics.
- [x] Confirm whether the model beats persistence on held-out data; report honestly if it does not.
**Acceptance:** an internship reviewer can run the collector, reproduce the holdout evaluation, inspect forecast errors, and see the data coverage and limitations. Do not claim a forecast improvement without held-out evidence.

## Work protocol
Complete one milestone at a time. At each handoff, update this file and `05-DECISIONS-AND-PROGRESS.md` with changes, commands run, outcomes, and next exact task. Never mark a milestone done without its acceptance checks.
