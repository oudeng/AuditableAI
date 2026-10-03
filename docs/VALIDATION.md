# Validation of release candidate 1.0.0rc1

Executed on **2026-10-04 (Japan time)** for candidate **1.0.0rc1**, using Python 3.12.14 on macOS arm64. The scientific environment is recorded in [`requirements-tested.txt`](../environments/requirements-tested.txt). These are author-workspace reproduction checks, not an independent laboratory replication or a user study.

## Checks actually performed

| Check | Result | What was exercised |
|---|---|---|
| Shared model implementation | Pass | Numerical module byte-identical to the original application module |
| Shared finite auditor | Pass | All five extracted function definitions match the original abstract syntax trees |
| Scientific/dependency tests | 8 passed | Native-coordinate equivalence, missing inputs, gate semantics and specific audit omissions |
| Artificial audit example | Pass | Three valid/equivalent bundles retained; seven invalid bundles rejected by Full; the strong conventional arm also passes |
| Offline figure route | Pass | 25 PNG/SVG figure pairs and five LaTeX table fragments generated |
| VERA recovery reaggregation | Pass | Mean seed-median difference 0.158626734; exact two-sided p = 0.0625 from five seed blocks; retained intervals checked |
| Official Japan retrieval | Pass | Nine NDB workbooks and one census workbook match original hashes, including NDB11 archive/member verification |
| Full Japanese reproduction | Pass | Extraction, candidate selection, six methods, temporal/geographical evaluation, verification, post-hoc diagnosis and five figure pairs |
| Official NHANES retrieval | Pass | All nine CDC modules match original hashes and have unique participant keys within each module |
| Full NHANES reproduction | Pass | Three split seeds × five selected families, held-out cycle scoring, finite audit and all 15 selected-model replay/selection checks |
| Isolated directory check | Pass | A copy outside the dissertation tree runs all eight tests, demo and 25 offline figures without the original manuscript/evidence directories |
| Python package build | Pass | Local wheel build and installation to an isolated target, without installing or changing scientific dependencies |
| Release inventory | Pass | Packaged file hashes, selected aggregate relationships, source-view hashes and prohibited-file/path/credential-pattern checks |

The source-checkout launcher is the documented reproduction interface; the experiment/data/figure assets are kept in the checkout. The wheel check validates package metadata and buildability, not a separately published PyPI distribution. These local checks preceded the initial GitHub publication. Subsequent hosted workflow results are available in the [repository Actions page](https://github.com/oudeng/AuditableAI/actions); they are separate from the local validation reported here.

## Fresh outputs versus historical results

The included reports can be regenerated with `japan-compare` and `nhanes-compare` after the corresponding fitting/verification stages. They compare counts and settings exactly, and continuous values with **absolute tolerance 1e-9, relative tolerance zero**. They exclude runtime, timestamps and changed serialization/source identities.

- [Japanese comparison report](../provenance/validation/japan_reference_comparison.json): all 60 metric rows, paired intervals, temporal and seven-region candidate-selection results, annual errors, gate activity and error decomposition agree exactly as parsed. All selected configurations match. Source-cell verification covers **5,922** strata; **48** retained-model replays, **188** claim records and **12** task/route checks pass. The gate overpredicts 187 of 188 standardized test quantities, as in the dissertation.
- [NHANES comparison report](../provenance/validation/nhanes_reference_comparison.json): all **30** metric rows, counts, selected configurations, primary bootstrap results and subgroup summaries agree within floating-point precision. Maximum absolute discrepancy is **6.483702463810914e-14**. Audit-arm/mechanism counts match exactly. The primary gate RMSE remains 1.0052599286 and boosted-tree RMSE 1.0101045412.

Bitwise equality of refitted pickle files is neither required nor claimed. The Japanese historical run and this refit used the same numerical environment; the NHANES historical server used Python 3.10.19, while this check used Python 3.12.14. The tolerance is a comparison rule, not a claim that every future platform will satisfy it.

## Figure checks

The combined offline and Japanese routes generate all **22 dissertation figures**, plus eight supporting repository figures. The framework preview and the new aggregate-only Japanese comparison were visually inspected. Existing figure generators retain the original plotting logic and scientific captions, with portable input/output locations. This is not a claim that every regenerated page of the dissertation was rendered or that raster bytes match a particular PDF.

## Routes not executed in this packaging session

- **Clinical raw-data extraction, refitting and external scoring were not rerun.** The portable clinical route is provided for authorized users. Its shared numerical code, unchanged checker functions, retained aggregate values and figure generation were checked; this is not end-to-end clinical validation of the port.
- The combined `examples` stage needs both fitted applications and was not rerun from clinical records. Its retained aggregate illustration results were used to regenerate the four corresponding figures.
- Original RPS/LGO/VERA/CaST training experiments were not repeated. The package supplies declared mathematical illustrations, aggregate redraws and the VERA cell reaggregation; full source-study environments remain upstream.
- No human pilot study, deployment evaluation, semantic ground-truth authentication, or causal pandemic analysis was added.

## Interpretation

Both Full and the strong conventional checker retain all 270 valid controls and reject all 630 injected invalid variants in each retained application. The concrete incremental result is relative to omitted checks: 180 target-scope/outcome-unit misses without scope, and 90 reference-identifier misses without dependency binding. The Japanese model's poor predictive performance is retained and diagnosed; reproduction does not turn it into a predictive gain.
