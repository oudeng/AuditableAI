import copy
import unittest
import numpy as np
from auditableai.models import Model
from auditableai.audit import ARMS, create_cases, inspect, digest, canonical
from auditableai.records import ClaimRecord

class TestAuditDependencies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=np.random.default_rng(19);cls.x=rng.normal(size=(256,2));y=1/(1+np.exp(-cls.x[:,0]))
        cls.model=Model('nhanes','gate',{'slope':1.,'reg':1.},19).fit(cls.x,y)
        cls.export=cls.model.export(['x','y'])
        cls.stale=Model('nhanes','gate',{'slope':2.,'reg':1.},19).fit(cls.x,y).export(['x','y'])
        cls.scope={'target':'artificial','outcome_unit':'arbitrary','data_scope':'synthetic'}
    def test_specific_missing_dependencies(self):
        cases=list(create_cases(self.export,self.stale,self.x,self.model.predict(self.x),self.scope,.2))
        misses={a:[] for a in ARMS}
        for family,bundle,ref,invalid in cases:
            for a in ARMS:
                found=inspect(bundle,ref,self.x,a)
                if not invalid:self.assertEqual(found,[])
                elif not found:misses[a].append(family)
        self.assertEqual(misses['Full'],[])
        self.assertEqual(misses['B1_conventional'],[])
        self.assertEqual(misses['minus_scope'],['scope_target','scope_unit'])
        self.assertEqual(misses['minus_dependency'],['reference_mismatch'])
    def test_canonical_identity_preserves_reordering(self):
        e=copy.deepcopy(self.export);e['terms'].reverse();e['comment']='harmless'
        self.assertEqual(digest(canonical(e)),digest(canonical(self.export)))
        e['intercept']+=1
        self.assertNotEqual(digest(canonical(e)),digest(canonical(self.export)))
    def test_false_input_label_is_outside_retained_probe_audit(self):
        # New-batch units are absent from this interface. A clean retained bundle
        # must not magically detect the unseen mislabeled batch.
        reference={'export':self.export,'model_id':digest(canonical(self.export)),'scope':self.scope}
        bundle={**reference,'host_predictions':self.model.predict(self.x)}
        self.assertEqual(inspect(bundle,reference,self.x,'Full'),[])
    def test_all_seven_fields_affect_identity(self):
        c=ClaimRecord('assertion',{}, {}, {}, {}, {}, 'boundary')
        a=c.to_dict()
        self.assertEqual(set(a)-{'record_sha256'}, {'clm','scp','art','ref','pro','evd','bnd'})
        for field in ['clm','scp','art','ref','pro','evd','bnd']:
            with self.subTest(field=field):
                revised=copy.deepcopy(c)
                setattr(revised,field,'revised text' if field in ['clm','bnd'] else {'revision':1})
                self.assertNotEqual(a['record_sha256'],revised.to_dict()['record_sha256'])

if __name__=='__main__':unittest.main()
