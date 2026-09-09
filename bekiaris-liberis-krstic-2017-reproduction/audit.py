"""Original-plant audit of Bekiaris-Liberis & Krstic, TAC 2017.
Eqs. 82-84 are stepped, NOT generated from a target trajectory. Eqs. 89-98
are sampled/ZOH; predictors are reconstructed from X and issued history.
Exact held-input unicycle flow; RK4 for the second spatial predictor.
"""
from __future__ import annotations
import argparse,hashlib,json,platform,time,os
from pathlib import Path
import numpy as np
from numba import njit
from scipy.integrate import solve_ivp
@njit(cache=True)
def nominal(t,x):
 c=np.cos(x[2]);s=np.sin(x[2]);M=x[0]*c+x[1]*s;Q=x[0]*s-x[1]*c
 w=-M*M*np.cos(t)-M*Q*(1+np.cos(t)**2)-x[2]
 return np.array([w,-M+Q*(np.sin(t)-np.cos(t))+Q*w])
@njit(cache=True)
def flow(x,w,v,h):
 a=w*h/2;sinc=1. if abs(a)<1e-12 else np.sin(a)/a
 return np.array([x[0]+v*h*sinc*np.cos(x[2]+a),x[1]+v*h*sinc*np.sin(x[2]+a),x[2]+2*a])
@njit(cache=True)
def lookup(U,q,dt,known):
 if q < -1e-10:return 0.,0.
 i=int(np.floor(q/dt+1e-9))
 if i<0:return 0.,0.
 if i>known:raise ValueError('Future issued-input access')
 return U[i,0],U[i,1]
@njit(cache=True)
def next_switch(q,dt):
 if q < -1e-10:return -q
 j=int(np.floor(q/dt+1e-9));return (j+1)*dt-q
@njit(cache=True)
def first_predictor(t,x,U,known,dt,D1,D2):
 p=x.copy();r=0.
 while r<D1-1e-10:
  q1=t+r-D1;q2=t+r-D2
  w=lookup(U,q1,dt,known)[0];v=lookup(U,q2,dt,known)[1]
  h=min(D1-r,next_switch(q1,dt),next_switch(q2,dt))
  if h<1e-12:raise ValueError('Degenerate predictor bin')
  p=flow(p,w,v,h);r+=h
 return p
@njit(cache=True)
def rhs_second(s,p,v):
 return np.array([v*np.cos(p[2]),v*np.sin(p[2]),nominal(s,p)[0]])
@njit(cache=True)
def second_predictor(t,p1,U,known,dt,D1,D2,ratio,wrong_clock):
 p=p1.copy();r=D1
 while r<D2-1e-10:
  q=t+r-D2;v=lookup(U,q,dt,known)[1]
  h=min(D2-r,next_switch(q,dt),dt*ratio)
  s=t+r if not wrong_clock else t+r-D2
  k1=rhs_second(s,p,v);k2=rhs_second(s+h/2,p+h*k1/2,v)
  k3=rhs_second(s+h/2,p+h*k2/2,v);k4=rhs_second(s+h,p+h*k3,v)
  p=p+h*(k1+2*k2+2*k3+k4)/6;r+=h
 return p
@njit(cache=True)
def physical_interval(t,x,U,k,dt,D1,D2,h):
 r=0.;y=x.copy()
 while r<h-1e-10:
  q1=t+r-D1;q2=t+r-D2
  w=lookup(U,q1,dt,k)[0];v=lookup(U,q2,dt,k)[1]
  z=min(h-r,next_switch(q1,dt),next_switch(q2,dt))
  if z<1e-12:raise ValueError('Degenerate physical bin')
  y=flow(y,w,v,z);r+=z
 return y
@njit(cache=True)
def _simulate(dt,T,D1,D2,x0,mode,ratio,wrong_clock):
 n=int(np.ceil(T/dt));ts=np.minimum(np.arange(n+1)*dt,T)
 X=np.empty((n+1,3));X[0]=x0;U=np.zeros((n+1,2));P1=np.full((n+1,3),np.nan);P2=P1.copy()
 for k in range(n+1):
  t=ts[k]
  if mode==0:
   p1=first_predictor(t,X[k],U,k-1,dt,D1,D2)
   p2=second_predictor(t,p1,U,k-1,dt,D1,D2,ratio,wrong_clock)
   P1[k]=p1;P2[k]=p2
   U[k,0]=nominal(t+D1,p1)[0];U[k,1]=nominal(t+D2,p2)[1]
  else:U[k]=nominal(t,X[k])
  if not np.isfinite(U[k]).all() or np.max(np.abs(U[k]))>1e12:
   raise RuntimeError('Numerical guard: command > 1e12 or nonfinite')
  if k<n:X[k+1]=physical_interval(t,X[k],U,k,dt,D1,D2,ts[k+1]-t)
 return ts,X,U,P1,P2

def simulate(dt=.01,T=101.,D1=.5,D2=1.,x0=(.5,.5,.5),mode='predictor',ratio=.5,wrong_clock=False):
 if not (np.isfinite([dt,T,D1,D2,ratio]).all() and dt>0 and T>0 and 0<=D1<=D2 and ratio>0):raise ValueError('Invalid parameters')
 if mode not in ('predictor','uncompensated','delay_free'):raise ValueError(mode)
 x0=np.asarray(x0,dtype=float)
 if x0.shape!=(3,) or not np.isfinite(x0).all():raise ValueError('Invalid x0')
 if mode=='delay_free':D1=D2=0.
 return _simulate(dt,T,D1,D2,x0,0 if mode=='predictor' else 1,ratio,wrong_clock)

def dense_physical(r,queries,D1,D2):
 t,x,u,_,_=r;dt=t[1]-t[0];rows=[]
 for q in np.atleast_1d(queries):
  j=min(int(np.floor(q/dt+1e-9)),len(t)-1)
  rows.append(physical_interval(t[j],x[j],u,len(t)-1,dt,D1,D2,max(0.,q-t[j])))
 return np.array(rows)

def metrics(r,D1,D2):
 t,x,u,p1,p2=r
 out={'final_time':float(t[-1]),'final_state':x[-1].tolist(),'final_norm':float(np.linalg.norm(x[-1])),
 'initial_control':u[0].tolist(),'max_abs_control':np.max(abs(u),axis=0).tolist(),'max_state_norm':float(np.linalg.norm(x,axis=1).max())}
 for name,d,p in [('P1',D1,p1),('P2',D2,p2)]:
  m=t+d<=t[-1]+1e-10;xf=dense_physical(r,t[m]+d,D1,D2)
  if np.isfinite(p).all():out[name+'_identity_max_component']=float(abs(p[m]-xf).max())
 if np.isfinite(p1).all():
  m=t>=D2-1e-10;xD=dense_physical(r,[D2],D1,D2)[0]
  def f(s,y):
   z=nominal(s,y);return [z[1]*np.cos(y[2]),z[1]*np.sin(y[2]),z[0]]
  ref=solve_ivp(f,(D2,t[-1]),xD,t_eval=t[m],method='DOP853',rtol=1e-11,atol=1e-13)
  out['post_D2_nominal_reference_error']=float(abs(x[m]-ref.y.T).max())
 return out

def plot(r,out,stem):
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 for data,labels,ylabel,kind in [(r[1],['X1','X2','X3'],'Physical state','state'),(r[2],['U1','U2'],'Issued command','input')]:
  fig,ax=plt.subplots(figsize=(8,4.2))
  for i,label in enumerate(labels):ax.plot(r[0],data[:,i],label=label,linewidth=1)
  ax.set(xlabel='Time (s)',ylabel=ylabel,title=stem);ax.legend();ax.grid(alpha=.25)
  fig.tight_layout();fig.savefig(out/(stem+'_'+kind+'.png'),dpi=160);plt.close(fig)

def main(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 cases=[(f'predictor_h{h}',dict(dt=h)) for h in [.04,.02,.01,.005,.0025]]
 cases += [(f'uncompensated_h{h}',dict(dt=h,T=15.,mode='uncompensated')) for h in [.01,.005,.0025,.00125,.000625,.0003125,.00015625]]
 cases += [('delay_free',dict(dt=.0025,T=100.,mode='delay_free')),('offgrid',dict(dt=.01,T=20.,D1=.503,D2=1.007)),
 ('spatial_refinement',dict(dt=.01,ratio=.25)),('wrong_clock_diagnostic',dict(dt=.005,wrong_clock=True)),('long_horizon',dict(dt=.01,T=500.))]
 results=[];runs={}
 for name,kw in cases:
  start=time.time()
  try:
   r=simulate(**kw);m=metrics(r,kw.get('D1',.5),kw.get('D2',1.));m.update(case=name,parameters=kw,status='completed',seconds=time.time()-start)
   np.savetxt(out/(name+'.csv'),np.column_stack(r),delimiter=',',header='t,X1,X2,X3,U1,U2,P1X1,P1X2,P1X3,P2X1,P2X2,P2X3',comments='');runs[name]=r
   if name in ('predictor_h0.0025','uncompensated_h0.0025','wrong_clock_diagnostic','long_horizon'):plot(r,out,name)
  except Exception as e:m=dict(case=name,parameters=kw,status='error',error=repr(e),seconds=time.time()-start)
  results.append(m);print(json.dumps(m),flush=True)
 (out/'summary.json').write_text(json.dumps(results,indent=2))
 if 'predictor_h0.0025' in runs:
  fine=runs['predictor_h0.0025'];comparison=[]
  for name,r in runs.items():
   if name.startswith('predictor_') or name in ('spatial_refinement','wrong_clock_diagnostic'):
    ref=np.column_stack([np.interp(r[0],fine[0],fine[1][:,j]) for j in range(3)])
    comparison.append(dict(case=name,max_component_difference_to_finest=float(abs(r[1]-ref).max())))
  (out/'refinement.json').write_text(json.dumps(comparison,indent=2))
 import scipy,numba
 (out/'provenance.json').write_text(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'numba':numba.__version__,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'execution':'CPU Python; no MATLAB','execution_environment':('Google Colab' if 'COLAB_RELEASE_TAG' in os.environ else 'GitHub Actions' if os.environ.get('GITHUB_ACTIONS')=='true' else 'Other Python runtime'),'author_code':False},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',default='results');main(ap.parse_args().out)
