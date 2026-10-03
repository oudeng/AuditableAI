# Dissertation figure and table map

Basis: manuscript v1.0, with the current chapter/appendix labels checked on 2026-10-04. Numbering is a locator, not an artifact identity; the filenames and source hashes are the more durable reference. Output roots below are relative to the selected working directory.

All 22 dissertation figures have generators. `figures` recreates 17 of them from included aggregates or mathematical definitions and also produces eight supplementary repository illustrations. `japan-figures`, after the complete Japanese workflow, recreates the other five. No original publisher image is embedded.

## Figures in the dissertation

Generators below are under [`figures/`](../figures/). The offline stage is `python scripts/reproduce.py figures`.

| Figure | Output under `figures/` (PNG and SVG) | Generator | Input / meaning |
|---|---|---|---|
| 3.1 | `framework_integrated` | `framework_integrated.py` | Original framework synthesis; README preview is copied from this output |
| 3.2 | `mechanisms/audit_execution_loop` | `integration_mechanisms.py` | Examination loop; conceptual |
| 4.1 | `mechanisms/rps_operation` | `integration_mechanisms.py` | RPS evaluation and decision mechanism |
| 4.2 | `mechanisms/rps_certificate` | `integration_mechanisms.py` | Artificial distributions illustrating the local certificate |
| 5.1 | `lgo_operator_family` | `ch04_ch05.py` | Logistic functions and derivatives, evaluated analytically |
| 5.2 | `mechanisms/lgo_operation` | `integration_mechanisms.py` | Expression construction and examination |
| 5.3 | `lgo_published_components` | `ch04_ch05.py` | Published standardized expression parameters; no patient data |
| 6.1 | `mechanisms/vera_same_host` | `integration_mechanisms.py` | Same-host reference and information conditions |
| 6.2 | `vera_faithfulness` | `ch06_ch07.py` | Redraw of retained faithfulness summaries |
| 6.3 | `vera_recovery` | `ch06_ch07.py` | Reaggregation of released AUROC cells; five independent seed blocks |
| 7.1 | `mechanisms/cast_protocols` | `integration_mechanisms.py` | Artificial ontology illustrating protocol visibility |
| 7.2 | `mechanisms/cast_fusion` | `integration_mechanisms.py` | Final four-source/five-feature fusion |
| 7.3 | `cast_inductive` | `ch06_ch07.py` | Retained final-system aggregate means |
| 8.1 | `phase4c/external_comparisons` | `phase4c_examples.py` | Frozen clinical/NHANES paired contrasts |
| 8.2 | `phase4c/example_time` | `phase4c_examples.py` | Fixed clinical model, two laboratory-availability rules |
| 8.3 | `phase4c/example_population` | `phase4c_examples.py` | Fixed clinical model, changed evaluation population |
| 8.4 | `phase4c/example_units` | `phase4c_examples.py` | NHANES waist-unit mismatch and normalization |
| 8.5 | `japan_health/japan_workflow` | `japan_health.py` | Japanese workflow; run `japan-figures` after rebuilding data and results |
| 8.6 | `japan_health/japan_prefectures` | `japan_health.py` | Locally regenerated prefectural observations and forecasts |
| 8.7 | `japan_health/japan_review_time` | `japan_review1.py` | Locally regenerated annual patterns and errors |
| 8.8 | `japan_health/japan_review_activity` | `japan_review1.py` | Observed input distribution and frozen gate activity |
| 8.9 | `japan_health/japan_tokyo` | `japan_health.py` | Locally regenerated Tokyo report and source-cell trace |

The Japanese generators consume full locally generated outputs because the public repository omits the internal dataset and full record collection. The other generators explicitly read the historical `evidence/` view; running them after a new fit does not silently replace the reported snapshot.

## Generated dissertation tables

These are LaTeX fragments under `tables/`, not standalone documents. They use the dissertation's table packages and cross-reference labels; compilation into a different document requires the corresponding preamble and labels. No LaTeX installation is needed to generate them.

| Table | Output | Generator / stage |
|---|---|---|
| 8.2 | `phase4b_clinical.tex` | `phase4b_results.py` / offline `figures` |
| 8.3 | `phase4b_nhanes.tex` | Same |
| 8.4 | `phase4b_audit.tex` | Same |
| 8.5 | `phase4b_audit_mechanisms.tex` | `audit_mechanism_table.py` / offline `figures` |
| 8.6 | `phase4c_examples.tex` | `phase4c_examples.py` / offline `figures` |
| 8.7 | `japan_models.tex` | `japan_health.py` / `japan-figures` |
| 8.8 | `japan_gate_activity.tex` | `diagnose_review1.py`, captions finalized by `japan_review1.py` |
| 8.9 | `japan_error_decomposition.tex` | Same |
| 8.10 | `japan_tokyo.tex` | `japan_health.py` / `japan-figures` |
| 8.11 | `japan_reproduction.tex` | Same |
| A.3 | `japan_yearly_selection.tex` | `diagnose_review1.py`, captions finalized by `japan_review1.py` |
| A.4 | `japan_complete_record.tex` | `japan_review1.py` / `japan-figures` |

Conceptual tables and the published RPS summaries in Chapters 2–7/A.1 are authored manuscript material, not generated experiment tables. Table A.2 lists native gate parameters available in a fresh `japan_health/formal_v1/gate_expression.json`; the original table was typeset in the manuscript. This package does not claim to rebuild the entire dissertation PDF.

## Additional repository illustrations

The offline route also produces `rps_family_means`, `mechanisms/audit_interfaces`, five figures under `phase4b/` (`clinical_design`, `clinical_external`, `clinical_transport`, `nhanes_external`, `audit_ablation`), and `japan_aggregate_comparison`. These are useful supporting views; they are **not eight additional numbered figures in manuscript v1.0**. The final one is a new repository-only visualization of unchanged Japanese aggregate MAE values.

Most generators write input/output hashes under `checks/`. Hashes of ported source files differ from historical originals; the mechanism table checks the original source identity against both retained audit freezes and identifies the current runner separately. Figure byte hashes are environment dependent. Numeric evidence, transformation rules and inferential units are the reproducibility targets.
