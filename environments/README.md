# Environments

- `original-clinical-nhanes.json`: recorded Python and scientific-library versions for the original server application runs; no machine paths or GPU inventory.
- `original-japan-python312.txt`: original local Japanese-study environment listing.
- `requirements-tested.txt`: full package listing for the environment actually used to validate this candidate.
- `../requirements.txt`: portable installation constraints used by the quick start.

These tabular models and plots use CPU numerical libraries; they do not require PyTorch, Julia or a GPU. The four original studies have their own environments in their upstream repositories.

Numerical portability is verified at the result level. Exact pickled binaries, timestamps, runtime costs and rendered-image hashes need not match across platforms. Do not load another user's untrusted model pickle.
