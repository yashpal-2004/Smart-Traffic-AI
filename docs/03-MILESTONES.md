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

## M2 — Q-learning agent (IN PROGRESS)
- [x] Define discrete observation encoding and legal actions.
- [x] Implement Q-table, epsilon-greedy policy, training loop, checkpoint format.
- [x] Log episode reward and core metrics.
**Acceptance:** train/evaluate separation exists; agent can complete episodes without invalid actions; learning curve is reproducible for fixed seeds.

## M3 — Evaluation and evidence (IN PROGRESS)
- [x] Compare fixed-time and RL on matched seeds and at least three demand patterns.
- [x] Report mean, median, spread, sample count, and definitions.
- [x] Reserve held-out seeds; reward tuning remains future work.
**Acceptance:** results exportable; no cherry-picked single-run claims; README includes limitations and actual measured results.

## M4 — Backend API (IN PROGRESS)
- [x] Create run/step/control/evaluation endpoints and schema validation.
- [x] Add clear error responses and in-memory run state.
**Acceptance:** API can drive a complete deterministic run and return metrics; API docs reflect actual behavior.

## M5 — Premium frontend (IN PROGRESS)
- [x] Build responsive Simulate, Compare, Learn pages.
- [x] Add intersection visualization, run controls, metric cards, controller comparison, educational explanations.
- [x] Add empty/error handling, keyboard-operable controls, reduced motion.
**Acceptance:** core workflow usable without reading source; visualization agrees with backend snapshots; no placeholder metrics.

## M6 — Polish and release (NOT STARTED)
- [ ] Add setup docs, screenshots/GIF, architecture diagram, sample evaluation export.
- [ ] Review responsive layouts and accessibility.
- [ ] Run requested verification and document results.
**Acceptance:** clean clone setup works; all claims trace to reproducible results; limitations are visible.

## Work protocol
Complete one milestone at a time. At each handoff, update this file and `05-DECISIONS-AND-PROGRESS.md` with changes, commands run, outcomes, and next exact task. Never mark a milestone done without its acceptance checks.
