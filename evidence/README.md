# Included reference evidence

These are selected historical aggregates used in the dissertation, plus a native-coordinate export fitted to public NHANES data for its gate illustration. They are not complete original run directories.

| Directory | Included material | Deliberately not distributed |
|---|---|---|
| `phase4b/` | Clinical/NHANES metric and bootstrap summaries, cohort flow counts, audit-arm aggregates, reportable metrics, primary NHANES expression | Patient/participant rows, hospital IDs, splits, probes, full predictions, clinical model parameters, private artifact inventory |
| `phase4c/` | Aggregate time/population/unit illustration results | Individual predictions and source paths |
| `japan_health/` | Six-method metrics, aggregate candidate-selection scores, paired intervals, yearly error and activity summaries, exact yearly error decomposition, reproduction task summaries | Raw workbooks, 5,922-row input panel, per-prefecture outputs and complete record collection |
| `papers/vera/` | Released faithfulness summary and synthetic recovery benchmark cells | Clinical rows, trained weights, original training pipeline |
| `papers/cast/` | Final-system aggregate comparison and final-system freeze table | Embeddings, indexes, query records or a claim of upstream release equivalence |
| `papers/rps/` | 18 published family means with source locator | Encounter logs or newly estimated uncertainty |
| `papers/lgo/` | Two published standardized component parameters | Clinical fitted-model file or natural-unit cutoff claims |

Original fingerprints and public-view fingerprints are recorded separately. Existing historical hash values inside these snapshots still refer to their original evidence; they are not expected to match the newly ported Python files. `scripts/reproduce.py check` verifies the packaged view against the release manifest and checks numerical relationships.

Do not replace these files with new fitted outputs without defining and documenting a new scientific snapshot. Current run output is written to the working directory.
