"""Scientific invariants for native export, train-only transforms and binary basis."""
import unittest
import numpy as np
from scipy.special import expit
from auditableai.models import Model,GateBasis,Preprocessor,native_predict

class TestScientificInvariants(unittest.TestCase):
    def test_native_export_missing_and_shifted_inputs(self):
        rng=np.random.default_rng(7);X=rng.normal(size=(500,3));X[:,0]*=100;X[:,1]=rng.integers(0,2,500);X[::13,2]=np.nan
        for task,y in [('nhanes',2+expit(X[:,0]/50)+rng.normal(0,.1,500)),('clinical',rng.binomial(1,expit(X[:,0]/100)))]:
            m=Model(task,'gate',{'slope':2.,'reg':1.},7).fit(X,y)
            E=X[:80].copy();E[:,0]*=3;E[1,0]=np.nan;E[2,:]=np.nan
            np.testing.assert_allclose(m.predict(E),native_predict(m.export(['a','b','c']),E),rtol=1e-12,atol=1e-12)
    def test_transform_is_not_refit_on_test(self):
        p=Preprocessor().fit(np.array([[1.,0],[3.,1],[np.nan,0]]));before=p.export()
        p.transform(np.array([[1e9,np.nan]]));self.assertEqual(before,p.export());self.assertEqual(p.median_[0],2)
    def test_binary_has_no_duplicate_gates(self):
        x=np.column_stack([np.arange(20),np.arange(20)%2,np.zeros(20)])
        b=GateBasis().fit(x);self.assertEqual(len(b.terms_),3);self.assertEqual(b.linear_,[1,2])
    def test_manual_native_expression(self):
        e={'preprocessing':{'medians':[10.]},'terms':[[0,.2,10.,3.]],'linear':[[1,2.]],'intercept':-1.,'link':'identity'}
        np.testing.assert_allclose(native_predict(e,np.array([[10.],[np.nan]])),[.5,2.5])

if __name__=='__main__':unittest.main()
