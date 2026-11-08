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

## M3 — Evaluation and evidence (NOT STARTED)
- [ ] Compare fixed-time and RL on matched seeds and at least three demand patterns.
- [ ] Report mean, median, spread, sample count, and definitions.
- [ ] Tune reward/phase settings only against training/validation seeds; reserve held-out seeds.
**Acceptance:** results exportable; no cherry-picked single-run claims; README includes limitations and actual measured results.

## M4 — Backend API (NOT STARTED)
- [ ] Create run/step/control/evaluation endpoints and schema validation.
- [ ] Add clear error responses and persistence strategy (in-memory first).
**Acceptance:** API can drive a complete deterministic run and return metrics; API docs reflect actual behavior.

## M5 — Premium frontend (NOT STARTED)
- [ ] Build responsive Simulate, Compare, Learn, About pages.
- [ ] Add intersection visualization, run controls, metric cards, charts, educational explanations.
- [ ] Add loading/empty/error/completed states, keyboard access, reduced motion.
**Acceptance:** core workflow usable without reading source; visualization agrees with backend snapshots; no placeholder metrics.

## M6 — Polish and release (NOT STARTED)
- [ ] Add setup docs, screenshots/GIF, architecture diagram, sample evaluation export.
- [ ] Review responsive layouts and accessibility.
- [ ] Run requested verification and document results.
**Acceptance:** clean clone setup works; all claims trace to reproducible results; limitations are visible.

## Work protocol
Complete one milestone at a time. At each handoff, update this file and `05-DECISIONS-AND-PROGRESS.md` with changes, commands run, outcomes, and next exact task. Never mark a milestone done without its acceptance checks.
