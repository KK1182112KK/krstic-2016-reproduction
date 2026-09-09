"""Independent continuous-time DDE reference for UNCOMPENSATED physical plant.
Method of steps + DOP853 dense history. Not used in the predictor controller.
"""
from pathlib import Path
import json,time
import numpy as np
from scipy.integrate import solve_ivp
from audit import nominal

def simulate(T=15.,rtol=1e-10):
 seg=[];ends=[];y0=np.array([.5,.5,.5])
 def state(q):
  if q<=1e-12:return np.array([.5,.5,.5])
  j=min(int(np.floor((q-1e-11)/.5)),len(seg)-1)
  if j<0:raise ValueError('History outside previous method-of-steps segments')
  return seg[j].sol(q)
 for a in np.arange(0,T,.5):
  b=min(T,a+.5)
  def rhs(t,x):
   s=min(t,b-1e-12)
   w=0. if s<.5 else nominal(s-.5,state(s-.5))[0]
   v=0. if s<1. else nominal(s-1.,state(s-1.))[1]
   return [v*np.cos(x[2]),v*np.sin(x[2]),w]
  sol=solve_ivp(rhs,(a,b),y0,method='DOP853',rtol=rtol,atol=rtol*.01,max_step=.01,dense_output=True)
  if not sol.success:raise RuntimeError(sol.message)
  seg.append(sol);ends.append(b);y0=sol.y[:,-1]
 ts=np.linspace(0,T,15001);xs=np.array([state(t) for t in ts])
 return ts,xs
if __name__=='__main__':
 out=Path('results');out.mkdir(exist_ok=True);res=[]
 for tol in [1e-8,1e-10,1e-12]:
  t,x=simulate(rtol=tol);np.savetxt(out/f'uncompensated_continuous_tol{tol}.csv',np.column_stack([t,x]),delimiter=',',header='t,X1,X2,X3',comments='')
  m={'rtol':tol,'final_state':x[-1].tolist(),'final_norm':float(np.linalg.norm(x[-1]))};res.append(m);print(m,flush=True)
 (out/'continuous_reference.json').write_text(json.dumps(res,indent=2))
