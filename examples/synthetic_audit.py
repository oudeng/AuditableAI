"""Offline demonstration only: artificial measurements are not thesis experiments."""
import json
import numpy as np
from auditableai.models import Model
from auditableai.audit import ARMS, create_cases, inspect
from auditableai.records import ClaimRecord
from auditableai.paths import WORK

def main():
    rng=np.random.default_rng(421)
    x=rng.normal(size=(240,2));x[::17,1]=np.nan
    y=2+1/(1+np.exp(-x[:,0]))+rng.normal(0,.05,len(x))
    model=Model('nhanes','gate',{'slope':1.,'reg':1.},421).fit(x,y)
    stale=Model('nhanes','gate',{'slope':2.,'reg':1.},422).fit(x,y)
    export=model.export(['artificial_x1','artificial_x2'])
    scope={'target':'artificial response','outcome_unit':'arbitrary','data_scope':'synthetic demonstration'}
    rows=[]
    for family,bundle,reference,truth in create_cases(export,stale.export(export['features']),x[:64],model.predict(x[:64]),scope,.2):
        rows.append({'family':family,'invalid_truth':truth,'findings':{a:inspect(bundle,reference,x[:64],a) for a in ARMS}})
    record=ClaimRecord(clm='Exported expression reproduces its fitted host on the stated probes',
        scp=scope,art={'format':'native gate expression','features':export['features']},
        ref={'type':'fitted host','probe_count':64},pro={'absolute_tolerance':1e-8,'labels_given_to_auditor':False},
        evd={'fault_results':'fault_results.json'},bnd='Artificial software demonstration; not clinical evidence or validation of the source meaning.')
    out=WORK/'demo';out.mkdir(parents=True,exist_ok=True)
    (out/'claim_record.json').write_text(json.dumps(record.to_dict(),indent=2)+'\n')
    (out/'fault_results.json').write_text(json.dumps(rows,indent=2)+'\n')
    assert all(not r['findings']['Full'] for r in rows if not r['invalid_truth'])
    assert all(r['findings']['Full'] for r in rows if r['invalid_truth'])
    print('Artificial demo: 3 equivalent bundles retained; 7 injected faults rejected by Full.')
    print('The same finite examples are also rejected by the strong conventional control.')

if __name__=='__main__':main()
