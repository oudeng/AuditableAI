# Maintaining a release

## After reviewing local changes

1. Edit code/docs in this candidate, leaving historical reference results unchanged unless you explicitly define a new scientific version.
2. Use a fresh working directory for changed experiments. Record data fingerprints, environment and selection rules.
3. Update the source-map change description for any additional adaptation; never replace its original source hash with the current file hash.
4. Run tests and affected reproduction stages, then update the validation record with actual observations.
5. After reviewing the changes, refresh the inventory and check it:

```bash
python scripts/update_manifest.py
python scripts/reproduce.py check
```

An inventory mismatch is expected after editing. Regenerating hashes is not a substitute for reviewing the change or validating its scientific consequences.

## At the first public release

The public repository is [`oudeng/AuditableAI`](https://github.com/oudeng/AuditableAI). Publish changes after author review. Upload the curated source tree, not the surrounding dissertation workspace or working output directory. Keep `.gitignore` and the provenance documents. Inspect staged filenames before committing; a clean new history avoids accidentally including older sensitive derivatives.

Set a release tag only after the final content is fixed. Add the real repository URL, commit/tag, release date and any completed archival DOI to `CITATION.cff`, README and manuscript evidence references. Do not invent a DOI or claim an independent archive before deposit succeeds. Keep released tags immutable; corrections receive a new version and change note.

The CI configuration runs hosted checks; see [Actions](https://github.com/oudeng/AuditableAI/actions) for the status of each commit. Its smoke checks use no patient data. Public-data downloads and complete experiments are deliberately separate from every-push CI.

## Content that stays local

Raw data, person-level derivatives, split/probe arrays, fitted clinical weights, all working directories, institutional application forms, unpublished review correspondence and the internal NDB dataset are outside this code release. The original four study repositories remain separate.
