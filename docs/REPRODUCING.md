# Reproducing the dissertation evidence

Run commands from the repository root after the README installation. Each stage prints its progress and raises an error on failed consistency checks. The launcher sets `PYTHONHASHSEED=0` and single-thread numerical settings before importing numerical libraries in the child process.

## 1. Offline route

```bash
python scripts/reproduce.py check
python scripts/reproduce.py test
python scripts/reproduce.py demo
python scripts/reproduce.py figures
```

`check` verifies the release inventory, aggregate arithmetic and admitted-fault counts. `test` checks scientific and dependency invariants. `demo` creates an artificial example, a seven-field record and findings. `figures` uses the included aggregate snapshots and mathematical illustrations; it does not download data, fit clinical models or recreate all four source studies.

Output locations: `work/demo/`, `work/figures/`, `work/tables/` and `work/checks/`. The figure map lists the subset that appears in the dissertation and labels additional illustrations. Exact raster bytes can vary with plotting libraries and fonts; scientific values are checked independently.

## 2. Japan NDB and census

```bash
export AUDITABLEAI_WORKDIR=/path/to/fresh/japan_reproduction
python scripts/reproduce.py japan-fetch
python scripts/reproduce.py japan-prepare
python scripts/reproduce.py japan-fit
python scripts/reproduce.py japan-verify
python scripts/reproduce.py japan-diagnose
python scripts/reproduce.py japan-figures
python scripts/reproduce.py japan-compare
```

The working path is an example; choose a writable directory. The downloader verifies every official file against the study fingerprint, including the selected workbook inside the NDB11 ZIP. If official bytes change, it stops and preserves changed bytes separately. Do not relax a hash check just to obtain a successful run.

| Stage | Main outputs under the work directory |
|---|---|
| Fetch | `japan_health/raw/`, `retrieval_report.json` |
| Prepare | `japan_health/processed/waist_panel.csv`, `census_weights.csv`, `ndb2019_weights.csv`, extraction checks |
| Fit | `japan_health/formal_v1/`: candidate scores, 48 model files, temporal/spatial predictions, metrics, gate expression |
| Verify | 5,922 source-derived strata checked, 48 retained-model replays, 188 claim records, 12 task/route checks |
| Diagnose | `japan_health/review1_v1/`: annual errors, gate activity, exact term decomposition, seven-field record revisions |
| Figures | Five Japanese dissertation figures and related LaTeX tables |

The six forecast methods, rolling FY2020/FY2021 selection, final FY2017–2021 fit, FY2022/FY2023 tests and seven geographical holdouts remain as defined in the original protocol. FY2023 predictions use the observed FY2022 history; this is not recursive forecasting from a 2021 origin. The data are revised published vintages, not a fully vintage-correct historical simulation.

Diagnosis uses frozen final models. It refits earlier-year validation models only with the already selected configurations to check retained selection scores; it does not select another model after seeing test errors. Baseline `persistence.pkl` and `trend.pkl` both serialize `None`; their distinct rules live in code and the selected damping parameter, not in those identical pickle hashes.

The full set of source cells and locally generated datasets remains in your working directory. This repository does not distribute the separate internal `NDB_dataset` package.

## 3. NHANES

```bash
export AUDITABLEAI_WORKDIR=/path/to/fresh/application_reproduction
python scripts/reproduce.py nhanes-fetch
python scripts/reproduce.py nhanes-fit
python scripts/reproduce.py nhanes-audit
python scripts/reproduce.py nhanes-verify
python scripts/reproduce.py nhanes-compare
```

All nine DEMO/BMX/GHB modules for 2013–2014, 2015–2016 and 2017–2018 are downloaded with expected hashes. The portable package fixes an operational gap in the original server-only downloader, which assumed six modules already existed.

Five families share the original features, split seeds and selection budget. Models are saved before the external cycle is loaded for scoring. The formal outputs are `runs/nhanes_formal_v1/`; the audit subdirectory contains 900 bundles × eight arms. Verification goes to `runs/nhanes_verification_v1/`. Primary intervals are paired participant bootstrap intervals, conditional on the evaluated cohort. MEC-weighted summaries are descriptive, not national survey inference.

## 4. Clinical data, for authorized users

```bash
export AUDITABLEAI_WORKDIR=/path/to/fresh/application_reproduction
export MIMIC_IV_ZIP=/authorized/path/mimic-iv-3.1.zip
export EICU_DIR=/authorized/path/eicu-crd/2.0
python scripts/reproduce.py clinical-extract
python scripts/reproduce.py clinical-fit
python scripts/reproduce.py clinical-audit
python scripts/reproduce.py clinical-verify
```

The extractor expects the original MIMIC ZIP prefix `mimic-iv-3.1/` and eICU `patient.csv.gz`/`lab.csv.gz`. It reads the archive in chunks but retains selected laboratory events in memory, so it is not a bounded-memory streaming implementation. Budget disk for the source archive and derived outputs, and use a research workstation/server with adequate RAM. This route does not request credentials or upload results.

The task predicts subsequent hospital mortality among adults still in their first eligible ICU stay at 24 hours. The original selection, laboratory-unit whitelist, sampling and availability window, and patient-disjoint splits are preserved. eICU's revision offset is an availability proxy. Hospital-cluster resampling retains the original independent-unit convention. Constant-predictor joint calibration coefficients are suppressed in the verification report because they are not identifiable.

All person-level cohorts, splits, predictions, probes, fitted weights and native clinical exports stay in the local working directory. `.gitignore` is a guard, not permission to redistribute them.

## 5. Three explanatory examples

After **both** clinical and NHANES fits and their verification stages in the same working directory:

```bash
python scripts/reproduce.py examples
```

This uses the saved models, not new fitting. It reconstructs the cohort-selection and unit-conversion examples; the strict/measurement-time comparison already lives in the clinical summary. The examples are exploratory explanatory extensions, not additional confirmatory experiments. The offline figure route can redraw their recorded aggregate outcomes without patient access.

## New runs and historical evidence

Use a new working directory for each full attempt. Rerunning an already completed fitting or diagnostic stage is intentionally blocked. Package source hashes differ from historical scripts because paths and interfaces were adapted. New freezes explicitly identify reproduction runs. Historical aggregate snapshots under `evidence/` remain unchanged by execution.

`japan-compare` and `nhanes-compare` compare newly generated summaries against the included reference evidence and write machine-readable reports under `work/checks/`. Counts, labels and selected settings must match exactly; continuous outputs use absolute tolerance 1e-9 and relative tolerance zero. Timing, timestamps and serialized model hashes are excluded. A failed comparison calls for investigation, not silent replacement of reference evidence.

Cross-environment refits need not be bitwise identical. Compare sample counts, chosen candidates, metrics and recorded tolerances. See [validation](VALIDATION.md) for what was actually rerun during packaging, including any untested routes. Loading pickle files is appropriate only for artifacts you generated and trust; this repository ships no pickles.
