#!/usr/bin/env python3
"""Run a documented reproduction stage from a source checkout."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO/'src'))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=['check', 'test', 'demo', 'figures', 'japan-fetch',
        'japan-prepare', 'japan-fit', 'japan-verify', 'japan-diagnose', 'japan-figures',
        'japan-compare', 'nhanes-compare', 'nhanes-fetch', 'nhanes-fit', 'nhanes-audit', 'nhanes-verify',
        'clinical-extract', 'clinical-fit', 'clinical-audit', 'clinical-verify', 'examples'])
    p.add_argument('--workdir', type=Path, help='Fresh output/data workspace; default: repository/work')
    a=p.parse_args()
    if a.workdir: os.environ['AUDITABLEAI_WORKDIR']=str(a.workdir.expanduser().resolve())
    from auditableai.paths import WORK, prepare_outputs
    prepare_outputs()
    env=os.environ.copy()
    # These are set before every child interpreter imports numerical libraries.
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', PYTHONHASHSEED='0', MPLBACKEND='Agg',
               MPLCONFIGDIR=str(WORK/'cache/matplotlib'), XDG_CACHE_HOME=str(WORK/'cache'))
    env['PYTHONPATH']=str(REPO/'src')+os.pathsep+env.get('PYTHONPATH','')
    commands={
        'check':[['scripts/verify_release.py']],
        'test':[['-m','unittest','discover','-s',str(REPO/'tests'),'-v']],
        'demo':[['examples/synthetic_audit.py']],
        'figures':[[f'figures/{n}.py'] for n in ['framework_integrated','integration_mechanisms',
            'ch04_ch05','ch06_ch07','phase4b_results','phase4c_examples','audit_mechanism_table','japan_summary']],
        'japan-fetch':[['scripts/fetch_japan.py']],
        'japan-compare':[['scripts/compare_reproduction.py','japan']],
        'nhanes-compare':[['scripts/compare_reproduction.py','nhanes']],
        'japan-prepare':[['experiments/japan_health/prepare_data.py']],
        'japan-fit':[['experiments/japan_health/run_formal.py']],
        'japan-verify':[['experiments/japan_health/verify_and_package.py']],
        'japan-diagnose':[['experiments/japan_health/diagnose_review1.py']],
        'japan-figures':[['figures/japan_health.py'],['figures/japan_review1.py']],
        'nhanes-fetch':[['scripts/fetch_nhanes.py']],
        'examples':[['experiments/phase4c/run_examples.py']],
        'clinical-extract':[['experiments/phase4b/extract_clinical.py']],
    }
    for task in ['clinical','nhanes']:
        commands[task+'-fit']=[['experiments/phase4b/run_formal.py',task,task+'_formal_v1']]
        commands[task+'-audit']=[['experiments/phase4b/audit_challenges.py',task,task+'_formal_v1']]
        commands[task+'-verify']=[['experiments/phase4b/verify_results.py',task]]
    for command in commands[a.stage]:
        if command[0]!='-m':command[0]=str(REPO/command[0])
        subprocess.run([sys.executable,*command],cwd=REPO,env=env,check=True)

if __name__=='__main__':main()
