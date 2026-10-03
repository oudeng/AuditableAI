# Data definitions and access

## Clinical application

Sources: [MIMIC-IV 3.1](https://physionet.org/content/mimiciv/3.1/) and [eICU-CRD 2.0](https://physionet.org/content/eicu-crd/2.0/). Obtain your own authorized access under the respective source requirements. No credentials or clinical rows are included or downloaded by this repository.

The reference experiment contains 53,439 MIMIC adults and 99,441 eICU adults from 207 hospitals. Inputs are age, sex, creatinine, glucose, potassium, sodium, bicarbonate, hemoglobin, platelets and white-cell count. The observed information window ends at the 24-hour landmark. The source outcome is subsequent in-hospital mortality, not 24-hour mortality. See the complete [protocol](../experiments/phase4b/protocol.json) for eligibility, one-patient selection, units and availability rules.

Only selected aggregate results are included: overall scores, sufficiently aggregated calibration summaries, subgroup summaries and cohort flows. Source paths, hospital identifiers and private artifact inventories have been removed from the public views. No trained clinical parameter export is bundled. Full local runs create sensitive derivatives that must remain outside a public release.

## NHANES application

The [CDC NHANES](https://wwwn.cdc.gov/nchs/nhanes/default.aspx) public DEMO, BMX and GHB modules provide adults with measured HbA1c. Training/development uses 2013–2016 (11,131 people); the external test uses 2017–2018 (5,261). Input units are age in years, sex indicator, BMI in kg/m², waist circumference in cm and income-to-poverty ratio. HbA1c is in percent; prediction errors are percentage points.

[`nhanes_sources.json`](../data_manifests/nhanes_sources.json) lists all nine URLs and the hashes recorded by the experiment. No participant rows are committed. The included primary NHANES gate export is fitted to public data and is used only to redraw the documented BMI-gate curves.

## Japanese health application

Sources: [MHLW NDB Open Data](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html) releases 3–11 and [2020 Census table 2-7](https://www.e-stat.go.jp/stat-search/files?stat_infid=000032142410). The source manifest supplies direct official files and exact study hashes.

The indicator is the share meeting waist circumference ≥85 cm for males or ≥90 cm for females **among recorded waist examinees aged 40–74**, in residential prefecture and fiscal-year-end age bands. It is not resident prevalence, metabolic syndrome prevalence or a person-level diagnosis. The panel has 47 prefectures × 2 sexes × 7 age bands × 9 fiscal years = 5,922 rows. No linkage across individuals or reconstruction of suppressed counts is attempted.

| Generated column | Meaning |
|---|---|
| `year`, `release` | Checkup fiscal year and NDB publication release; different concepts |
| `pref_id`, `prefecture` | Stable ordered prefecture ID and source label |
| `sex`, `age` | Male/female; lower bound of five-year age band |
| `n` | Sum of the three published waist-category counts in that stratum |
| `y` | Counts meeting the sex-specific criterion |
| `rate` | `y / n`, stored as a proportion |
| `complete` | Whether published source cells provide usable nonnegative counts |
| `source_file`, `sheet`, `source_cells`, `source_sha256` | Exact lineage to the official workbook |

Male numerators combine the ≥90 and 85–<90 categories; female numerators use ≥90 only. 2020 census national age counts supply **sex-specific reference weights**, not denominators. The fixed FY2019 examinee weights form a sensitivity analysis. These distinctions are encoded in both extraction and a separately implemented raw-cell oracle.

`japan-prepare` writes CSV files locally. The public repository includes download recipes and aggregate evaluation summaries, not the internally shared dataset, raw workbooks, full per-prefecture predictions, or all 188 records. `japan-verify` regenerates the full records locally; `japan-diagnose` adds the post-hoc boundary and diagnosis fields. The complete record printed in the dissertation can therefore be rebuilt from official sources.

## Terms and publication boundary

MIT applies to the software, not source data or original publications. Attribute CDC, MHLW, Statistics Bureau/e-Stat and the relevant clinical database creators when using their resources. Check the sources' current terms for your intended use. This repository does not grant source-data rights.

Downloaded files and generated rows/weights/predictions are excluded from version control. A future dataset release is a separate decision from publishing this code. No institutional forms, signatures, manuscript PDFs or reviewer correspondence are part of this repository.
