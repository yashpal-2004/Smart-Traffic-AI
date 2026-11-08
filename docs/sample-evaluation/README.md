# Sample evaluation exports

- `sample-evaluation.json` is the complete API report, including protocol, source/configuration metadata, checkpoint hashes, episode records, paired deltas, and intervals.
- `sample-evaluation.csv` contains the same report as typed rows (`protocol`, `controller_summary`, `paired_summary_pooled`, `paired_summary_scenario`, `paired_delta`, and `episode`). Episode objects are stored as JSON in `details_json`.

Protocol: 500 simulation steps, seeds 101/202/303/404/505, and balanced, rush-hour, and northbound-surge scenarios. The controller summaries contain 15 matched scenario/seed episodes per controller. Report ID, generation time, source revision, and local Q-table fingerprints are embedded in the JSON and protocol rows.

The included checkpoint files are local and are not part of the repository. The fingerprints identify the saved tables used when this sample was generated; they cannot recreate those models on a clean clone. Treat this as a reproducible report record for the committed source and local checkpoint metadata, not as a promise that a fresh training run will produce identical learned weights.
