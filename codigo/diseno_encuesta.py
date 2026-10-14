"""Clase Design del análisis nacional, conservada sin modificar."""
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import t

class Design:
 def __init__(self,df,domain):
  self.df=df;self.domain=np.asarray(domain,bool);self.w=df.fact_cal_esi.to_numpy(float)
  self.psu,self.keys=pd.factorize(pd.MultiIndex.from_frame(df[['estrato','conglomerado_correlativo']]),sort=True)
  self.H,self.hkeys=pd.factorize(self.keys.get_level_values(0),sort=True)
  self.J=len(self.keys);self.nh=np.bincount(self.H);self.fac=np.divide(self.nh,self.nh-1,out=np.zeros(len(self.nh),float),where=self.nh>1)
  self.B=self.agg(self.w*self.domain);self.N=self.B.sum()
  self.gdl=len(np.unique(self.psu[self.domain]))-len(np.unique(df.estrato[self.domain]))
  self.crit=t.ppf(.975,self.gdl)
 def agg(self,z):return np.bincount(self.psu,weights=z,minlength=self.J)
 def variance(self,z):
  sums=np.bincount(self.H,weights=z,minlength=len(self.nh))
  ss=np.bincount(self.H,weights=z*z,minlength=len(self.nh))
  return max(0.,np.sum(self.fac*(ss-sums*sums/self.nh)))
 def mean(self,y):
  A=self.agg(self.w*self.domain*np.nan_to_num(y));m=A.sum()/self.N
  return m,np.sqrt(self.variance((A-m*self.B)/self.N))
 def event(self,event):
  e=np.asarray(event,bool)&self.domain;n=int(e.sum());A=self.agg(self.w*e);tot=A.sum();p=tot/self.N
  se=np.sqrt(self.variance((A-p*self.B)/self.N));setot=np.sqrt(self.variance(A))
  gdl=int(len(np.unique(self.psu[e]))-len(np.unique(self.df.estrato[e]))) if n else 0
  crit_total=t.ppf(.975,gdl) if gdl>0 else np.nan
  if 0<p<1 and se>0:lo,hi=expit(logit(p)+np.array([-1,1])*self.crit*se/(p*(1-p)))
  elif p==0 or p==1:lo=hi=np.nan
  else:lo=hi=p
  maxee=min(p,1-p)**(2/3)/9
  # INE proportion rule uses denominator-domain sample size/df.
  qprop='no fiable' if self.domain.sum()<60 or self.gdl<9 or n==0 else ('fiable' if se<=maxee else 'poco fiable')
  cvtot=setot/tot*100 if tot>0 else np.nan
  qtot='no fiable' if n<60 or gdl<9 or cvtot>30 else ('poco fiable' if cvtot>15 else 'fiable')
  # Conservative reporting also requires >=60 observed tail/bin cases and total reliability.
  qdetail='fiable' if qprop=='fiable' and qtot=='fiable' else ('poco fiable' if qtot=='poco fiable' and qprop!='no fiable' else 'no fiable')
  wt=self.w[e];imp=(self.df.imp_d1_monto.eq(1)|self.df.imp_d5_monto.eq(1)).to_numpy()
  return dict(n_muestra=n,personas=tot,porcentaje=100*p,ee_pp=100*se,ic95_inf_pct=100*lo,ic95_sup_pct=100*hi,
   cv_pct=100*se/p if p>0 else np.nan,ee_personas=setot,ic95_inf_personas=max(0,tot-crit_total*setot) if gdl>0 else np.nan,ic95_sup_personas=tot+crit_total*setot if gdl>0 else np.nan,
   cv_total_pct=cvtot,psu_evento=int((A>0).sum()),estratos_evento=int(len(np.unique(self.df.estrato[e]))),gdl_evento=gdl,n_efectivo_kish_evento=tot*tot/(wt@wt) if n else 0,
   calidad_proporcion_INE=qprop,calidad_total_INE=qtot,resolucion_defendible=qdetail,
   peso_max_caso_pct=100*wt.max()/tot if n else np.nan,peso_top5_casos_pct=100*np.sort(wt)[-5:].sum()/tot if n else np.nan,
   peso_max_psu_pct=100*A.max()/tot if n else np.nan,imputados_n=int((e&imp).sum()),imputados_pct=100*self.w[e&imp].sum()/tot if n else np.nan)
