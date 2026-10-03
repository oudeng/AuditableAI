"""New thesis estimators; complete training transforms and native-unit exports."""
import numpy as np
from scipy.special import expit
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

class Preprocessor:
    def fit(self,X):
        self.median_=np.nanmedian(X,axis=0)
        self.median_=np.nan_to_num(self.median_,nan=0.)
        raw=self.raw(X); self.scaler_=StandardScaler().fit(raw)
        return self
    def raw(self,X):
        X=np.asarray(X,float)
        return np.column_stack([np.where(np.isnan(X),self.median_,X),np.isnan(X).astype(float)])
    def transform(self,X): return self.scaler_.transform(self.raw(X))
    def export(self):
        return {'medians':self.median_.tolist(),'mean':self.scaler_.mean_.tolist(),'scale':self.scaler_.scale_.tolist()}

class GateBasis:
    def __init__(self,slope=1.,single=False): self.slope=slope;self.single=single
    def fit(self,X):
        self.terms_=[];self.linear_=[]
        for j in range(X.shape[1]):
            if len(np.unique(X[:,j]))<=2: self.linear_.append(j)
            else:
                for midpoint in np.unique(np.quantile(X[:,j],[.5] if self.single else [.2,.5,.8])):
                    self.terms_.append((j,self.slope,float(midpoint)))
        return self
    def transform(self,X):
        cols=[expit(a*(X[:,j]-m)) for j,a,m in self.terms_]+[X[:,j] for j in self.linear_]
        return np.column_stack(cols)

class Model:
    def __init__(self,task,family,params,seed):
        self.task=task;self.family=family;self.params=params;self.seed=seed
    def fit(self,X,y):
        self.pre=Preprocessor().fit(X);Z=self.pre.transform(X)
        if self.family=='constant':self.mean=float(np.mean(y));return self
        if self.family in ['gate','single_gate']:
            self.basis=GateBasis(self.params['slope'],self.family=='single_gate').fit(Z);Z=self.basis.transform(Z)
        if self.family=='hgb':
            cls=HistGradientBoostingClassifier if self.task=='clinical' else HistGradientBoostingRegressor
            self.est=cls(**self.params,max_iter=150,l2_regularization=1,early_stopping=False,random_state=self.seed)
        elif self.task=='clinical': self.est=LogisticRegression(C=self.params['reg'],max_iter=3000,tol=1e-7,solver='lbfgs')
        else:self.est=Ridge(alpha=self.params['reg'])
        self.est.fit(Z,y);return self
    def predict(self,X):
        if self.family=='constant':return np.full(len(X),self.mean)
        Z=self.pre.transform(X)
        if hasattr(self,'basis'):Z=self.basis.transform(Z)
        return self.est.predict_proba(Z)[:,1] if self.task=='clinical' else self.est.predict(Z)
    def export(self,features):
        assert hasattr(self,'basis')
        coef=self.est.coef_.ravel();mean=self.pre.scaler_.mean_;scale=self.pre.scaler_.scale_
        terms=[[j,a/scale[j],mean[j]+scale[j]*m,float(coef[k])] for k,(j,a,m) in enumerate(self.basis.terms_)]
        offset=len(terms);linear=[];intercept=float(np.asarray(self.est.intercept_).ravel()[0])
        for k,j in enumerate(self.basis.linear_):
            w=coef[offset+k]/scale[j];linear.append([j,float(w)]);intercept-=w*mean[j]
        return {'features':features,'preprocessing':self.pre.export(),'terms':terms,'linear':linear,'intercept':intercept,'link':'logistic' if self.task=='clinical' else 'identity'}

def native_predict(export,X):
    X=np.asarray(X,float);m=np.array(export['preprocessing']['medians'])
    raw=np.column_stack([np.where(np.isnan(X),m,X),np.isnan(X).astype(float)])
    out=np.full(len(X),export['intercept'])
    for j,a,t,w in export['terms']:out+=w*expit(a*(raw[:,int(j)]-t))
    for j,w in export['linear']:out+=w*raw[:,int(j)]
    return expit(out) if export['link']=='logistic' else out

def candidates(family):
    if family=='constant':return [{}]
    if family=='linear':return [{'reg':float(x)} for x in np.logspace(-4,4,9)]
    if family=='hgb':return [{'learning_rate':a,'max_leaf_nodes':b} for a in [.03,.1,.2] for b in [7,15,31]]
    return [{'slope':a,'reg':r} for a in [.5,1.,2.] for r in [.1,1.,10.]]
