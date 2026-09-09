"""Artstein 1982 equation-to-numerics audit, original plants independently stepped.
The scanned source has no numerical plots; these are new equation tests, not
reproductions of author figures. Printed and derived alternatives stay separate.
"""
from __future__ import annotations
import argparse,hashlib,json,platform,time,os
from pathlib import Path
import numpy as np
from scipy.special import roots_legendre
from scipy.linalg import expm

_G={}
def integ(f,a,b,n=48):
 if abs(b-a)<1e-15:return 0.
 if n not in _G:_G[n]=roots_legendre(n)
 z,w=_G[n];q=(a+b)/2+(b-a)*z/2
 val=np.asarray(f(q))
 return (b-a)/2*np.sum(val*w,axis=-1)

def command(t):return np.sin(.7*np.asarray(t))+.3*np.cos(1.9*np.asarray(t))

def rk4(f,y0,T,h):
 n=int(round(T/h));t=np.linspace(0,T,n+1);x=np.empty((n+1,len(np.atleast_1d(y0))));x[0]=np.atleast_1d(y0)
 for k in range(n):
  s=t[k];dt=t[k+1]-s;y=x[k]
  a=f(s,y);b=f(s+dt/2,y+dt*a/2);c=f(s+dt/2,y+dt*b/2);d=f(s+dt,y+dt*c)
  x[k+1]=y+dt*(a+2*b+2*c+d)/6
 return t,x

def oscillator(h=.02,kappa=1.,delay=.7,T=6.):
 A=np.array([[0.,1.],[-kappa*kappa,0.]])
 def L(t):return integ(lambda v:np.array([np.sin(kappa*(v-delay))/kappa,np.cos(kappa*(v-delay))])*command(t-v),0,delay)
 bc=np.array([-np.sin(kappa*delay)/kappa,1+np.cos(kappa*delay)])
 bp=np.array([-np.sin(kappa*delay),1+np.cos(kappa*delay)])
 t,x=rk4(lambda s,x:A@x+np.array([0.,command(s)+command(s-delay)]),[1.,-.2],T,h)
 y0=x[0]+L(0.)
 _,yc=rk4(lambda s,y:A@y+bc*command(s),y0,T,h)
 _,yp=rk4(lambda s,y:A@y+bp*command(s),y0,T,h)
 yr=np.array([z+L(s) for s,z in zip(t,x)])
 return np.column_stack([t,x,yr,yc,yp]),{'derived_error':float(abs(yr-yc).max()),'printed_error':float(abs(yr-yp).max()),'derived_Bhat':bc.tolist(),'printed_Bhat':bp.tolist()}

def population(h=.05,T=10.):
 t,z=rk4(lambda s,z:np.array([z[0]+z[1],-4*np.exp(-s)-z[1]]),[1.,0.],T,h)
 yr=z[:,0]+z[:,1]/2;exact=(1+2*t)*np.exp(-t)
 return np.column_stack([t,z,yr,np.exp(-t),exact]),{'y_error':float(abs(yr-np.exp(-t)).max()),'x_error':float(abs(z[:,0]-exact).max()),'final_x':float(z[-1,0])}

def mixed(h=.02,nq=24,T=5.):
 A=.3;H=1.3;d=.8;b0=.4;b1=-.6
 def density(a):return .2+.1*a
 bhat=b0+b1*np.exp(-A*d)+integ(lambda a:np.exp(-A*a)*density(a),0,H,nq)
 def L(t):
  atom=b1*integ(lambda v:np.exp(A*(v-d))*command(t-v),0,d,nq)
  cont=integ(lambda a:np.array([density(q)*integ(lambda v:np.exp(A*(v-q))*command(t-v),0,q,nq) for q in a]),0,H,nq)
  return atom+cont
 def f(t,x):return A*x+b0*command(t)+b1*command(t-d)+integ(lambda a:density(a)*command(t-a),0,H,nq)
 t,x=rk4(f,[.4],T,h);_,y=rk4(lambda t,y:A*y+bhat*command(t),[.4+L(0)],T,h)
 yr=x[:,0]+np.array([L(s) for s in t])
 return np.column_stack([t,x,yr,y]),{'identity_error':float(abs(yr-y[:,0]).max()),'Bhat':float(bhat),'quadrature_nodes':nq}

def time_varying(h=.02,T=3.,nq=24):
 A=.2;H=.7
 def B(t,a):return .2+.1*t+.3*a
 def L(t):
  return integ(lambda a:np.array([integ(lambda v:np.exp(A*(v-q))*B(t-v+q,q)*command(t-v),0,q,nq) for q in a]),0,H,nq)
 def b(t,printed):return integ(lambda a:np.exp(-A*a)*B(t+a,t if printed else a),0,H,nq)
 t,x=rk4(lambda s,x:A*x+integ(lambda a:B(s,a)*command(s-a),0,H,nq),[.4],T,h)
 _,yc=rk4(lambda s,y:A*y+b(s,False)*command(s),[.4+L(0)],T,h)
 _,yp=rk4(lambda s,y:A*y+b(s,True)*command(s),[.4+L(0)],T,h)
 yr=x[:,0]+np.array([L(s) for s in t])
 return np.column_stack([t,x,yr,yc,yp]),{'derived_error':float(abs(yr-yc[:,0]).max()),'printed_error':float(abs(yr-yp[:,0]).max())}

def proportional(h=.02,T=5.):
 A=.3;b0=.4;b1=.8
 def L(t):return integ(lambda s:2*np.exp(A*(t-2*s))*b1*command(s),t/2,t)
 t,x=rk4(lambda s,x:A*x+b0*command(s)+b1*command(s/2),[.4],T,h)
 _,y=rk4(lambda s,y:A*y+(b0+2*b1*np.exp(-A*s))*command(s),[.4],T,h)
 yr=x[:,0]+np.array([L(s) for s in t])
 return np.column_stack([t,x,yr,y]),{'identity_error':float(abs(yr-y[:,0]).max())}

def folded(h=.005,T=1.):
 a0=.4;a1=.8;x0=.2
 def L(t):
  f=lambda r:np.exp(t-r)*a1*command(r*(1-r))
  if t>=.25:return integ(f,t,1.)
  z=np.sqrt(1-4*t);lo=(1-z)/2;hi=(1+z)/2
  return integ(f,t,lo)+integ(f,hi,1.)
 def derived(t):
  lower=np.sqrt(max(0.,1-4*t))
  term=.5*integ(lambda z:(np.exp(-(.5-z/2))+np.exp(-(.5+z/2)))*command((1-z*z)/4),lower,1.)
  return np.exp(t)*(x0+a0*integ(lambda s:np.exp(-s)*command(s),0,t)+a1*term)
 def printed(t):
  def f(s):
   z=np.sqrt(np.maximum(0,1-4*s));alpha=2*z*np.exp(s-.5)*(np.exp(z)-np.exp(-z))
   return np.exp(-s)*alpha*command(s)
  return np.exp(t)*(x0+a0*integ(lambda s:np.exp(-s)*command(s),0,t)+a1*integ(f,0,min(t,.25)))
 t,x=rk4(lambda s,x:x+a0*command(s)+a1*command(s*(1-s)),[x0],T,h)
 yr=x[:,0]+np.array([L(s) for s in t]);yc=np.array([derived(s) for s in t]);yp=np.array([printed(s) for s in t])
 return np.column_stack([t,x,yr,yc,yp]),{'derived_error':float(abs(yr-yc).max()),'printed_error':float(abs(yr-yp).max())}

def closed_loop(h=.02,T=12.,delay=.6):
 n=int(round(T/h));t=np.arange(n+1)*h;u=np.zeros(n+1);x=np.zeros(n+1);x[0]=1.;yr=np.zeros(n+1);ref=np.zeros(n+1);ref[0]=1.
 K=-2*np.exp(delay);bhat=np.exp(-delay)
 def lookup(q,k):
  if q<-1e-11:return 0.
  j=int(np.floor(q/h+1e-9))
  if j>k:raise ValueError('Future command')
  return u[j]
 def L(t,k):
  total=0.;start=max(0.,t-delay)
  while start<t-1e-11:
   j=int(np.floor(start/h+1e-9));end=min(t,(j+1)*h)
   if j>k:raise ValueError('Future command in transform')
   total+=u[j]*np.exp(t-delay-start)*(-np.expm1(-(end-start)))
   start=end
  return total
 for k in range(n+1):
  yr[k]=x[k]+L(t[k],k-1);u[k]=K*yr[k]
  if k==n:break
  r=t[k];xx=x[k]
  while r<t[k+1]-1e-11:
   q=r-delay
   next_t=delay if q<-1e-11 else delay+(int(np.floor(q/h+1e-9))+1)*h
   end=min(t[k+1],next_t);d=end-r;v=lookup(q,k)
   xx=np.exp(d)*xx+np.expm1(d)*v;r=end
  x[k+1]=xx;ref[k+1]=np.exp(h)*ref[k]+bhat*np.expm1(h)*u[k]
 return np.column_stack([t,x,u,yr,ref,np.exp(-t)]),{'same_input_identity_error':float(abs(yr-ref).max()),'continuous_feedback_reference_error':float(abs(yr-np.exp(-t)).max()),'final_x':float(x[-1]),'K':float(K),'delay':delay}

def sampled_oscillator():
 rows=[]
 for k in [1.,np.pi/2,np.pi,2*np.pi,3*np.pi]:
  A=np.array([[0.,1.],[-k*k,0.]]);F=expm(A)
  v=np.array([(1-np.cos(k))/(k*k),np.sin(k)/k])
  bcont=np.array([-np.sin(k)/k,1+np.cos(k)])
  bhat=np.array([(np.cos(2*k)-1)/(k*k),np.sin(2*k)/k])
  rows.append({'kappa_h':float(k),'continuous_rank':int(np.linalg.matrix_rank(np.column_stack([bcont,A@bcont]),tol=1e-10)),'sampled_rank':int(np.linalg.matrix_rank(np.column_stack([bhat,F@bhat]),tol=1e-10)),'held_physical_B':v.tolist(),'reduced_jump_B':bhat.tolist()})
 k=2*np.pi;A=np.array([[0.,1.],[-k*k,0.]]);x=np.array([1.,0.]);u=np.sin(np.arange(8))+1.;allrows=[]
 for j in range(8):
  v=u[j]+(u[j-1] if j else 0.)
  for r in np.linspace(0,1,51)[:-1]:
   xp=expm(A*r)@x+np.array([(1-np.cos(k*r))/k**2,np.sin(k*r)/k])*v;allrows.append([j+r,*xp,v])
  x=expm(A)@x+np.array([(1-np.cos(k))/k**2,np.sin(k)/k])*v
 allrows.append([8.,*x,u[-1]])
 return np.array(allrows),{'ranks':rows,'final_physical_state':x.tolist(),'interpretation':'Printed final condition excludes odd multiples only; sampled controllability actually requires sin(k*h) != 0.'}

def plot_table(table,out,stem,cols,labels,ylabel):
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(8,4.2))
 for j,l in zip(cols,labels):ax.plot(table[:,0],table[:,j],label=l,linewidth=1.2)
 ax.set(xlabel='Time',ylabel=ylabel,title=stem);ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(out/(stem+'.png'),dpi=160);plt.close(fig)

def main(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);results=[];cases=[]
 for k in [1.,2.]:
  for h in [.04,.02,.01]:cases.append((f'oscillator_k{k}_h{h}',oscillator,{'h':h,'kappa':k}))
 for name,func in [('population',population),('mixed',mixed),('time_varying',time_varying),('proportional',proportional),('closed_loop',closed_loop)]:
  for h in [.04,.02,.01]:cases.append((f'{name}_h{h}',func,{'h':h}))
 cases.append(('mixed_quadrature48',mixed,{'h':.01,'nq':48}));cases.append(('closed_loop_offgrid',closed_loop,{'h':.01,'delay':.613}))
 for h in [.01,.005,.0025]:cases.append((f'folded_h{h}',folded,{'h':h}))
 cases.append(('sampled_oscillator',sampled_oscillator,{}))
 for name,f,kw in cases:
  start=time.time()
  try:
   table,m=f(**kw);np.savetxt(out/(name+'.csv'),table,delimiter=',');m.update(case=name,parameters=kw,status='completed',seconds=time.time()-start)
   if name=='oscillator_k2.0_h0.01':plot_table(table,out,name,[3,5,7],['Reconstructed y1','Derived reduction y1','Printed Eq. 2.3 y1'],'Reduced state')
   if name=='closed_loop_h0.01':plot_table(table,out,name,[1,3],['Physical x','Reconstructed y'],'State')
   if name=='population_h0.01':plot_table(table,out,name,[1,3],['Physical x','Reconstructed y'],'State')
   if name=='time_varying_h0.01' or name=='folded_h0.0025':plot_table(table,out,name,[2,3,4],['Reconstructed y','General-theory coefficient','Printed example coefficient'],'Reduced state')
   if name=='sampled_oscillator':plot_table(table,out,name,[1,2],['Physical x1','Physical x2'],'Physical state, k*h = 2*pi')
  except Exception as e:m={'case':name,'parameters':kw,'status':'error','error':repr(e)}
  results.append(m);print(json.dumps(m),flush=True)
 (out/'summary.json').write_text(json.dumps(results,indent=2));import scipy
 (out/'provenance.json').write_text(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'execution':'CPU Python; no MATLAB','execution_environment':('Google Colab' if 'COLAB_RELEASE_TAG' in os.environ else 'GitHub Actions' if os.environ.get('GITHUB_ACTIONS')=='true' else 'Other Python runtime'),'author_code':False},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',default='results');main(ap.parse_args().out)
