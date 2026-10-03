# Provenance and adaptation

The package was prepared from the dissertation working code as of 2026-10-04. Its scientific reference is manuscript v1.0, including the later Japanese post-hoc diagnosis and the mechanism-by-audit-arm table. No retraining result from repository preparation replaces a manuscript number.

[`source_map.json`](../provenance/source_map.json) records each copied/adapted source, its original SHA-256, destination, packaged SHA-256 and change description. Source locators refer to the private dissertation workspace; they are provenance labels, not runtime dependencies. [`release_manifest.json`](../provenance/release_manifest.json) covers files in this candidate tree. These checksums establish content identity, not an independent no-later-than anchor or authorship certification.

## Intentional changes

1. Replace machine-specific paths with a configurable `AUDITABLEAI_WORKDIR` and clinical input environment variables.
2. Extract the unchanged additive model, finite auditor and seven-field record into a shared Python package.
3. Add a stage launcher, a complete nine-file NHANES downloader and pinned NDB/ZIP-member retrieval.
4. Redirect figure/table output away from the manuscript and remove dependence on private LaTeX source files. Small published numeric extracts retain their source identifiers.
5. Create public aggregate views by omitting private source paths, hospital identifiers and restricted artifact inventories. Preserve the original scientific numbers and separately identify the views.
6. Label fresh runs as reproductions. Preserve the original protocol documents and separate historical workflow statements from current executions.
7. Add meaningful invariant tests, an explicitly synthetic demonstration and release checks. None is reported as a new empirical validation of the dissertation framework.

The comparison rules, seeds, feature definitions, gate construction, candidate ordering, information splits and inferential units remain unchanged. Runtime measurements are machine-specific and are not human-efficiency evidence.

## Snapshot boundaries

- The clinical/NHANES frozen aggregates come from the dissertation's formal-v1 runs. The package does not contain their patient/participant-level inputs.
- VERA recovery cells and with-prior summaries come from the supplied VERA evidence bundle. Recovery reaggregation is executed; the original imputer and faithfulness experiments are not rerun here.
- RPS family means are small numeric extracts from the accepted manuscript. They are not recomputed encounter logs. The local source release lacks the logs needed to reconstruct certificate-versus-played-action results anew.
- LGO plots evaluate published formula components or analytical gate functions, not a new GP benchmark.
- CaST final five-signal tables come from the retained 2026-09-15 final-system snapshot and carry their own hashes. The public CaST repository's README may describe an earlier three-channel reproduction route. Do not substitute one snapshot for the other or call its release commit the commit that generated the dissertation table.
- Japanese reference summaries retain the poor predictive result and the post-hoc diagnosis. The internally packaged input dataset is excluded; the public-source recipe is included.

## Original and current environments

The clinical/NHANES experiments originally ran under Python 3.10.19 with the recorded server libraries. The Japanese experiment used the recorded Python 3.12 environment. Environment records are under `environments/`; `requirements.txt` describes the portable package's installation constraints. Exact environment records are historical descriptions, not a claim that all versions are available on every platform.

The actual packaging checks are described in [VALIDATION.md](VALIDATION.md). They distinguish fresh fitting, saved-artifact replay, aggregate re-tabulation and structural testing. The original full four-paper training pipelines remain in their respective repositories.
