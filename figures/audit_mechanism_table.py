from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Render the existing finite challenge by mechanism. No experiments are rerun."""
from pathlib import Path
import hashlib,json
base=EVIDENCE/'phase4b'
paths=[base/f'{task}_formal_v1/audit_v1/summary.json' for task in ['clinical','nhanes']]
docs=[json.loads(p.read_text()) for p in paths]
arms=docs[0]['freeze']['arms']; families=docs[0]['freeze']['families'][3:]
expected_arms=['B0_schema','B1_conventional','B2_no_binding','Full','minus_scope','minus_transform','minus_replay','minus_dependency']
assert arms==expected_arms and len(families)==7
matrices=[]
for d in docs:
 assert d['freeze']['arms']==arms
 matrix=[]
 for f in families:
  row=[]
  for a in arms:
   r=next(r for r in d['aggregates'] if r['family']==f and r['arm']==a)
   assert r['invalid_truth'] and r['n']==90
   row.append(r['n']-r['rejected'])
  matrix.append(row)
 matrices.append(matrix)
 assert all(sum(r['n']-r['rejected'] for r in d['aggregates'] if r['arm']==a and not r['invalid_truth'])==270 for a in arms)
assert matrices[0]==matrices[1]
mat=matrices[0];totals=[sum(row[j] for row in mat) for j in range(8)]
assert totals==[630,0,90,0,180,0,0,90]
assert all(v in [0,90] for row in mat for v in row)
misses={a:[f for f,r in zip(families,mat) if r[j]] for j,a in enumerate(arms)}
assert misses['minus_scope']==['scope_target','scope_unit']
assert misses['B2_no_binding']==misses['minus_dependency']==['reference_mismatch']
inactive=['scope_target','scope_unit','reference_mismatch','joint_stale']
slots=[30 if f in inactive else 90 for f in families];assert sum(slots)==390
names=['Target scope','Outcome unit','Gate coordinates','Coefficients','Reference identifier','Jointly stale artifacts','Added remote gate']
t=r'''\begin{table}[tbp]
\centering\footnotesize
\setlength{\tabcolsep}{3pt}
\caption[Accepted invalid variants by mechanism and audit arm]{Accepted invalid variants / submitted variants, per mechanism and audit arm. The clinical and NHANES applications have identical counts in every cell. The totals reproduce Table~\ref{tab:phase4b:audit}; all arms also retain all 270 valid controls.}
\label{tab:phase4b:audit-mechanisms}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.65cm}cc*{8}{r}@{}}
\toprule
Mechanism & Mag. & Slots & \makecell{Schema\\only} & \makecell{Conv.\\strong} & \makecell{Comp.\\unbound} & Full & \makecell{No\\scope} & \makecell{No\\transform} & \makecell{No\\replay} & \makecell{No\\dependency}\\
\midrule
'''
for f,name,s,row in zip(families,names,slots,mat):
 t+=name+' & '+('---' if f in inactive else '3')+f' & {s} & '+' & '.join(f'{n}/90' for n in row)+r'\\'+'\n'
t+=r'\midrule'+'\n'+'Total & --- & 390 & '+' & '.join(f'{n}/630' for n in totals)+r'\\'+'\n'+r'''\bottomrule
\end{tabular}
\par\smallskip
\begin{minipage}{\textwidth}\footnotesize
Mag. counts active magnitude settings; --- means the mutation ignores magnitude. Slots count model--probe--active-magnitude combinations after collapsing that redundant setting: 30 for four mechanisms and 90 for the other three. The 390 slots are neither independent fault draws nor a count of unique artifact mutations. Models, probes and mutation structures remain shared.
\end{minipage}
\end{table}
'''
out=TABLES/'phase4b_audit_mechanisms.tex';out.write_text(t)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
code=REPO/'experiments/phase4b/audit_challenges.py'
original=next(x for x in json.loads((REPO/'provenance/source_map.json').read_text()) if x['destination']=='experiments/phase4b/audit_challenges.py')
historical_match=all(original['source_sha256']==d['freeze']['source_sha256'] for d in docs)
assert historical_match
result={'kind':'Re-tabulation of frozen aggregates; no new trials','applications':['clinical','nhanes'],'arms':arms,'families':families,'accepted_per_family':mat,'submitted_per_family':90,'totals':totals,'missed_families':misses,'magnitude_invariant_families':inactive,'nominal_slots_after_collapsing_unused_magnitude':slots,'nominal_slot_total':390,'independence':'No independent sample size asserted; 390 is not an effective n','mechanism_source':display_path(code),'mechanism_source_sha256':h(code),'original_source_sha256':original['source_sha256'],'original_source_matches_both_frozen_code_hashes':historical_match,'ported_source_note':'The portable runner has a new hash; historical freezes refer to the original source identity, not this adapted runner.','sources':[{'path':display_path(p),'sha256':h(p)} for p in paths],'generator':display_path(Path(__file__)),'generator_sha256':h(Path(__file__)),'output':display_path(out),'output_sha256':h(out)}
(CHECKS/'v0.8_mechanism_matrix.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'matrix_shape':[7,8],'same_for_both_applications':True,'totals':totals,'historical_source_hashes_match':historical_match}))
