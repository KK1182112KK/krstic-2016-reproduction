"""Equation-to-simulation audit: Zhao et al., Automatica 144 (2022) 110479.

Traffic experiments integrate the ORIGINAL physical delay equations (42)/(47).
Predictors are reconstructed at every sample; the target never generates X.
'printed_product' evaluates g1(sigma2)=g2 via the paper's claimed consistency
identity. This is an explicitly disclosed closure of the printed future g1
term, NOT access to author code. 'gain_only' changes Eq. (30)'s K2 to K1;
'clock_consistent' also replaces Gamma2 by 1-D2'(P2)*g2.

Traffic coordinates: X in km, t in seconds; b=0.9/3600, u=86.4/3600.
For nonlinear traffic the bare coefficient of X^2 is interpreted as 1 in
these coordinates. An hourly-drift alternative is separately executable.
None of these conventions is silently asserted to be the authors' code.
"""
from __future__ import annotations
import argparse,json,hashlib,platform,time
from pathlib import Path
import numpy as np
from numba import njit

@njit(cache=True)
def delay(x,nonlinear):
    l=x+.2; d1=(l+.25*l*l)/.024 if nonlinear else l/.024
    d2=(.5-l)/.024; a=(1+.5*l)/.024 if nonlinear else 1/.024
    return d1,d2,a,-1/.024

@njit(cache=True)
def hist(U,q,k,dt,ch,h0,left_endpoint=False):
    now=k*dt
    if q>now+1e-9: raise ValueError('Predictor requires future issued input')
    if q<0 or (left_endpoint and abs(q-now)<1e-10 and k==0): return h0
    j=int(np.floor(q/dt+1e-9))
    if left_endpoint and j>=k:j=k-1
    if j<0:return h0
    return U[j,ch]

@njit(cache=True)
def prhs(s,p,U,k,dt,nonlinear,stage,variant,gamma):
    d1,d2,a,b=delay(p,nonlinear)
    if d1<=0 or d2<=0:raise ValueError('Predictor left physical positive-delay domain')
    h1=0. if nonlinear else 8.;h2=0. if nonlinear else 12.
    if stage==1:
        v1=hist(U,s,k,dt,0,h1,True)
        v2=hist(U,s+d1-d2,k,dt,1,h2,True)
        g=gamma*p*p-.00025*(v1+v2);den=1-a*g
    else:
        K1=80. if nonlinear else 90.;K2=50. if nonlinear else 60.
        # Eq. (30) prints B1*K2*P2. General Eq. (11) uses kappa1.
        gain=K2 if (not nonlinear and variant==0) else K1
        v2=hist(U,s,k,dt,1,h2,True)
        g=gamma*p*p-.00025*(gain*p+v2)
        den=1-b*g if variant==2 else (1-a*g)*(1-(b-a)*g)
    if not np.isfinite(den) or den<=1e-8:raise ValueError('Nonpositive/nonfinite predictor denominator; no clipping')
    return g/den,den

@njit(cache=True)
def integrate_predictor(p,lo,hi,U,k,dt,nonlinear,stage,variant,gamma,hs,order):
    if hi<lo-1e-9:raise ValueError('Negative sequential predictor interval')
    N=max(1,int(np.ceil((hi-lo)/hs)));h=(hi-lo)/N;mind=1e100
    for j in range(N):
        s=lo+j*h;f1,d=prhs(s,p,U,k,dt,nonlinear,stage,variant,gamma);mind=min(mind,d)
        if order==1:p+=h*f1;continue
        f2,d=prhs(s+h/2,p+h*f1/2,U,k,dt,nonlinear,stage,variant,gamma);mind=min(mind,d)
        f3,d=prhs(s+h/2,p+h*f2/2,U,k,dt,nonlinear,stage,variant,gamma);mind=min(mind,d)
        f4,d=prhs(s+h,p+h*f3,U,k,dt,nonlinear,stage,variant,gamma);mind=min(mind,d)
        p+=h*(f1+2*f2+2*f3+f4)/6
    return p,mind

@njit(cache=True)
def physical_rhs(t,x,U,k,dt,nonlinear,gamma):
    d1,d2,_,_=delay(x,nonlinear)
    if d1<=0 or d2<=0:raise ValueError('Physical trajectory left the positive-delay road domain')
    h1=0. if nonlinear else 8.;h2=0. if nonlinear else 12.
    return gamma*x*x-.00025*(hist(U,t-d1,k,dt,0,h1)+hist(U,t-d2,k,dt,1,h2))

@njit(cache=True)
def simulate_raw(dt,T,nonlinear,variant,gamma,spatial_ratio,physical_substeps,order):
    n=int(round(T/dt));X=np.zeros(n+1);P=np.zeros((n+1,2));U=np.zeros_like(P);den=np.zeros_like(P)
    X[0]=-.15 if nonlinear else .1
    K1=80. if nonlinear else 90.;K2=50. if nonlinear else 60.
    for k in range(n+1):
        t=k*dt;d1,d2,_,_=delay(X[k],nonlinear)
        p1,den1=integrate_predictor(X[k],t-d1,t,U,k,dt,nonlinear,1,variant,gamma,dt*spatial_ratio,order)
        da,db,_,_=delay(p1,nonlinear)
        p2,den2=integrate_predictor(p1,t-db+da,t,U,k,dt,nonlinear,2,variant,gamma,dt*spatial_ratio,order)
        P[k,0]=p1;P[k,1]=p2;U[k,0]=K1*p1;U[k,1]=K2*p2;den[k,0]=den1;den[k,1]=den2
        if k==n:break
        x=X[k];h=dt/physical_substeps
        for j in range(physical_substeps):
            s=t+j*h
            a=physical_rhs(s,x,U,k,dt,nonlinear,gamma)
            b=physical_rhs(s+h/2,x+h*a/2,U,k,dt,nonlinear,gamma)
            c=physical_rhs(s+h/2,x+h*b/2,U,k,dt,nonlinear,gamma)
            d=physical_rhs(s+h,x+h*c,U,k,dt,nonlinear,gamma)
            x+=h*(a+2*b+2*c+d)/6
        X[k+1]=x
    return np.arange(n+1)*dt,X,P,U,den

def simulate(dt=.05,T=None,nonlinear=False,variant='printed_product',gamma=None,spatial_ratio=.5,physical_substeps=4,order=4):
    if variant not in ['printed_product','gain_only','clock_consistent']:raise ValueError('Unknown variant')
    if T is None:T=160. if nonlinear else 200.
    if gamma is None:gamma=1. if nonlinear else 0.
    if not np.isfinite([dt,T,gamma,spatial_ratio]).all() or min(dt,T,spatial_ratio)<=0 or gamma<0:raise ValueError('Invalid numerical parameters')
    if abs(round(T/dt)*dt-T)>1e-9:raise ValueError('T must be an integer number of steps')
    return simulate_raw(dt,T,nonlinear,['printed_product','gain_only','clock_consistent'].index(variant),gamma,spatial_ratio,physical_substeps,order)

def inspect_run(name,par,r):
    t,x,p,u,den=r;nonlinear=par.get('nonlinear',False)
    errors=[];arrivals=[]
    for ch in [0,1]:
        d=np.array([delay(v,nonlinear)[ch] for v in p[:,ch]])
        future=t+d;mask=future<=t[-1]
        errors.append(float(np.max(abs(p[mask,ch]-np.interp(future[mask],t,x)))))
        clock=t-np.array([delay(v,nonlinear)[ch] for v in x])
        idx=np.flatnonzero(clock>=0)
        if len(idx) and idx[0]>0:
            k=idx[0];arrivals.append(float(t[k-1]-clock[k-1]*(t[k]-t[k-1])/(clock[k]-clock[k-1])))
        else:arrivals.append(None)
    return dict(case=name,parameters=par,completed=True,t_end=float(t[-1]),final_X_km=float(x[-1]),final_l_m=float(1000*(x[-1]+.2)),
                initial_P_km=p[0].tolist(),initial_U=u[0].tolist(),first_arrivals_seconds=arrivals,
                maximum_sampled_predictor_identity_errors_km=errors,minimum_evaluated_predictor_denominators=den.min(axis=0).tolist(),
                physical_nodes_violating_delay_order=int(sum(delay(v,nonlinear)[0]>delay(v,nonlinear)[1] for v in x)))

def exact_algebra_counterexample():
    """Literal Eq. (12), with future g1 evaluated from a KNOWN exact solution.

Audit-chosen genuine two-input plant f=-x+u1+u2; kappa1=kappa2=0;
zero inputs; X(t)=x0 exp(-t). All global structural hypotheses hold.
Not one of the paper's traffic examples. No closure g1(sigma2)=g2 is used.
"""
    from scipy.integrate import solve_ivp
    from scipy.optimize import brentq
    def Ds(p):return .3+.15*np.tanh(p),.6+.30*np.tanh(p),.15/np.cosh(p)**2,.30/np.cosh(p)**2
    rows=[]
    for x0 in [.2,.1,.05]:
        def exact_pred(s,ch):
            return brentq(lambda p:p-x0*np.exp(-s-Ds(p)[ch]),0,x0*np.exp(-s),xtol=1e-15)
        p1=exact_pred(0,0);d1,d2,_,_=Ds(p1);lo=d1-d2;expected=exact_pred(0,1)
        for tol in [1e-8,1e-10,1e-12]:
            def printed(s,y):
                p=y[0];d1,d2,a,b=Ds(p);sigma2=s+d2-d1
                g1=-exact_pred(sigma2,0);g2=-p
                return [g2/((1-a*g1)*(1-(b-a)*g2))]
            def corrected(s,y):
                p=y[0];b=Ds(p)[3];return [-p/(1+b*p)]
            pp=solve_ivp(printed,(lo,0),[p1],method='DOP853',rtol=tol,atol=tol*.01,max_step=.01).y[0,-1]
            pc=solve_ivp(corrected,(lo,0),[p1],method='DOP853',rtol=tol,atol=tol*.01,max_step=.01).y[0,-1]
            rows.append(dict(x0=x0,rtol=tol,printed_P2=float(pp),clock_consistent_P2=float(pc),exact_P2=float(expected),
                             printed_identity_error=float(pp-expected),clock_consistent_identity_error=float(pc-expected)))
    return dict(plant='dx/dt=-x+u1+u2; kappa1=kappa2=0; histories zero',
                delays='D1(x)=0.3+0.15*tanh(x); D2(x)=0.6+0.30*tanh(x)',
                exact_state='X(t)=x0*exp(-t)',
                algebra='Under the claimed identity g1(sigma2)=g2, printed Gamma2=1-b*g2+a*(b-a)*g2^2, while differentiation of P2=X(t+D2(P2)) requires Gamma2=1-b*g2.',rows=rows,
                scope='Counterexample to the stated predictor identity, not a demonstration of failure of every stabilization claim. No numerical value of psi(c) has been certified.')

def initial_arithmetic():
    from scipy.optimize import brentq
    b=.00025;speed=.024
    lin_first=.3/(speed+b*20)
    # Nonlinear pre-arrival state dictated by printed X^2 with zero histories.
    def xx(t):return -.15/(1+.15*t)
    first=brentq(lambda t:t-delay(xx(t),True)[0],0,10)
    return dict(linear_initial_delays_seconds=list(delay(.1,False)[:2]),linear_initial_rate_m_per_s=-1000*b*20,
                linear_first_incoming_arrival_seconds=lin_first,
                nonlinear_initial_delays_km_second_interpretation=list(delay(-.15,True)[:2]),
                nonlinear_initial_D1_meter_second_literal=(50+.25*50**2)/24,
                nonlinear_published_initial_D1_seconds=2.63,
                nonlinear_first_arrival_unforced_km_second=first,
                nonlinear_claimed_D1_difference=float(delay(-.15,True)[0]-2.63),
                Eq30='printed B1*K2*P2 versus B1*K1*P2 from (11),(25)',
                nonlinear_forward_complete_test='For zero inputs and X(0)>0: X(t)=X(0)/(1-X(0)t), finite escape. Assumption 3 is not global for (47).')

def plots(out,runs):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for nonlinear in [False,True]:
        kind='nonlinear' if nonlinear else 'linear'
        names=[kind+'_'+v+'_h0.025' for v in ['printed_product','clock_consistent']]
        if not nonlinear:names.insert(1,kind+'_gain_only_h0.025')
        for what in ['state','input']:
            fig,ax=plt.subplots(figsize=(8,4.5))
            for name in names:
                if name not in runs:continue
                t,x,p,u,den=runs[name];v=name.split(kind+'_')[1].split('_h')[0]
                if what=='state':ax.plot(t,1000*(x+.2),label=v)
                else:
                    ax.plot(t,u[:,0],label=v+' Uin');ax.plot(t,u[:,1],'--',label=v+' Uout')
            ax.set(xlabel='Time (s)',ylabel='Interface l (m)' if what=='state' else 'Density change (vehicles/km)',title=kind+' traffic: original physical plant')
            ax.legend(fontsize=8);ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(out/(kind+'_'+what+'.png'),dpi=160);plt.close(fig)
    # Reconstruct the transport fields from issued histories; not an independent PDE solve.
    for nonlinear in [False,True]:
        kind='nonlinear' if nonlinear else 'linear';name=kind+'_clock_consistent_h0.025'
        if name not in runs:continue
        t,x,p,u,den=runs[name];dt=t[1]-t[0];tt=np.linspace(0,t[-1],401);zz=np.linspace(0,.5,201)
        l=np.interp(tt,t,x)+.2;fields=np.zeros((len(zz),len(tt)))
        for j,z in enumerate(zz):
            Df=(z+.25*z*z)/.024 if nonlinear else z/.024;Dc=(.5-z)/.024
            for k,s in enumerate(tt):
                ch=0 if z<=l[k] else 1;query=s-(Df if ch==0 else Dc)
                base=32. if ch==0 else 128.;h0=0. if nonlinear else (8. if ch==0 else 12.)
                fields[j,k]=base+(h0 if query<0 else u[min(int(np.floor(query/dt+1e-9)),len(t)-1),ch])
        np.savez_compressed(out/(kind+'_transport.npz'),t=tt,z_km=zz,density=fields)
        fig,ax=plt.subplots(figsize=(8,4.5));im=ax.pcolormesh(tt,zz*1000,fields,shading='auto');ax.plot(tt,l*1000,label='Interface')
        ax.set(xlabel='Time (s)',ylabel='Road position (m)',title=kind+' transport reconstruction — clock-consistent variant')
        fig.colorbar(im,ax=ax,label='vehicles/km');fig.tight_layout();fig.savefig(out/(kind+'_transport.png'),dpi=160);plt.close(fig)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path('results'));args=ap.parse_args();out=args.out;out.mkdir(parents=True,exist_ok=True)
    cases=[]
    for nonlinear in [False,True]:
        for variant in (['printed_product','gain_only','clock_consistent'] if not nonlinear else ['printed_product','clock_consistent']):
            for h in [.1,.05,.025]:
                name=('nonlinear' if nonlinear else 'linear')+'_'+variant+'_h'+str(h)
                cases.append((name,dict(dt=h,nonlinear=nonlinear,variant=variant)))
    cases += [('nonlinear_hourly_drift',dict(dt=.05,nonlinear=True,variant='clock_consistent',gamma=1/3600)),
              ('linear_rectangle_rule',dict(dt=.05,variant='printed_product',order=1)),
              ('nonlinear_rectangle_rule',dict(dt=.05,nonlinear=True,variant='printed_product',order=1))]
    rows=[];runs={}
    for name,p in cases:
        start=time.perf_counter()
        try:
            r=simulate(**p);runs[name]=r;row=inspect_run(name,p,r)
            np.savetxt(out/(name+'.csv'),np.column_stack(r),delimiter=',',header='t,X_km,P1_km,P2_km,Uin,Uout,min_stage1_den,min_stage2_den',comments='')
        except Exception as exc:row=dict(case=name,parameters=p,completed=False,error=repr(exc))
        row['wall_seconds']=time.perf_counter()-start;rows.append(row);print(json.dumps(row),flush=True)
        (out/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n')
    (out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'algebra_counterexample.json').write_text(json.dumps(exact_algebra_counterexample(),indent=2)+'\n')
    (out/'source_arithmetic.json').write_text(json.dumps(initial_arithmetic(),indent=2)+'\n')
    import scipy,numba
    (out/'provenance.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,numba=numba.__version__,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),execution='Executed locally in ChatGPT container, not Colab/MATLAB/GitHub CI',method=__doc__),indent=2)+'\n')
    plots(out,runs)

if __name__=='__main__':main()
