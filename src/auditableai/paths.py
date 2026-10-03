"""One configurable working directory; no machine-specific paths."""
import os
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get('AUDITABLEAI_WORKDIR', str(REPO/'work'))).expanduser().resolve()
EVIDENCE = REPO/'evidence'
JAPAN = WORK/'japan_health'
FIGURES = WORK/'figures'
TABLES = WORK/'tables'
CHECKS = WORK/'checks'
def prepare_outputs():
    for p in [WORK, FIGURES, TABLES, CHECKS]: p.mkdir(parents=True, exist_ok=True)
def display_path(path):
    p=Path(path).resolve()
    if p.is_relative_to(WORK): return 'work/'+p.relative_to(WORK).as_posix()
    if p.is_relative_to(REPO): return 'repo/'+p.relative_to(REPO).as_posix()
    raise ValueError('Provenance source must be inside the repository or working directory')
def resolve_record_path(value):
    prefix, name=value.split('/', 1)
    root={'work':WORK, 'repo':REPO}[prefix]
    p=(root/name).resolve()
    if not p.is_relative_to(root): raise ValueError('Invalid provenance path')
    return p
def required_input(variable):
    value=os.environ.get(variable)
    if not value: raise SystemExit(f'Set {variable} to your authorized local data path; see docs/DATA.md.')
    path=Path(value).expanduser().resolve()
    if not path.exists(): raise SystemExit(f'{variable} does not exist: {path}')
    return path
