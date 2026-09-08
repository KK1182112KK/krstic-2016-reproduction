"""Direct physical DDE simulations for SCL 61 (2012), Eqs. 63-70.

Each stage evaluates the original plant and reconstructs the predictor from
current physical state plus past X2/v. No autonomous target-system state is
integrated. Explicit Heun in physical time, piecewise-linear state history,
and adaptive RK45 for the spatial predictor. This is a numerical approximation
of the continuous-time functional feedback, not an exact solution.

The printed Example 2 factor=1 and chain-rule factor=2 are separate experiments.
The physical delay is r*sin(w*s)**2 in BOTH. T_eq=.4 is an explicit hypothesis,
not a parameter stated in the cooling example's parameter sentence.
"""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp


class FeasibilityError(RuntimeError):
    pass


@dataclass
class StateDelayResult:
    t: np.ndarray
    X: np.ndarray
    U: np.ndarray
    P: np.ndarray
    predictor_denominator: np.ndarray
    phi: np.ndarray
    sigma_candidate: np.ndarray
    parameters: dict


def simulate(example: str = 'oscillatory', dt: float = .005,
             t_end: float = 6., factor: int = 1,
             x2_history: float | None = None, Teq: float = .4,
             predictor_rtol: float = 1e-8, predictor_atol: float = 1e-10,
             denominator_floor: float = 1e-6) -> StateDelayResult:
    """Return original X trajectories; raises, rather than clips, singular cases.

    X1(0)=1. Cooling defaults to the printed X2-history .2; oscillatory defaults
    to printed v-history .1. For a history-IC comparison pass .6 explicitly.
    predictor_denominator stores the endpoint denominator at accepted nodes;
    all spatial solver evaluations are guarded, but their minimum is not a
    certified global feasibility bound. sigma_candidate=P-based clock need not
    equal phi^{-1} for the printed factor=1 experiment.
    """
    if example not in ('cooling', 'oscillatory') or factor not in (1, 2):
        raise ValueError('Invalid example or factor (must be 1 or 2).')
    if x2_history is None:
        x2_history = .2 if example == 'cooling' else .1
    if (not np.isfinite([dt,t_end,x2_history,Teq,predictor_rtol,
                         predictor_atol,denominator_floor]).all()
        or min(dt,t_end,predictor_rtol,predictor_atol,denominator_floor)<=0
        or denominator_floor>=1):
        raise ValueError('Invalid numerical parameters.')
    if example == 'cooling' and (x2_history <= 0 or Teq <= 0):
        raise ValueError('Cooling experiment requires positive history and setpoint.')
    n = int(np.ceil(t_end/dt))
    ts=np.minimum(np.arange(n+1)*dt,t_end)
    xs=np.empty((n+1,2)); xs[0]=[1.,x2_history]
    us=np.empty(n+1); ps=np.empty(n+1); dens=np.empty(n+1)

    def delay(x):
        if example == 'oscillatory':
            return .3*np.sin(15*x)**2
        if x <= -1:
            raise FeasibilityError('Cooling delay is outside its domain X1 > -1.')
        return 1./(x+1.)

    def spatial_rhs(p,v):
        if example == 'oscillatory':
            derivative=factor*.3*15*np.sin(15*p)*np.cos(15*p)
            numerator=v
        else:
            if p <= -1:
                raise FeasibilityError('Cooling predictor left the delay domain.')
            derivative=-1./(p+1.)**2
            numerator=-(p-v)*(p+1.)
        den=1.-derivative*numerator
        if not np.isfinite(den) or den <= denominator_floor:
            raise FeasibilityError(f'Predictor denominator {den:.8g}; no clipping applied.')
        return numerator/den, den

    def evaluate(k, now, state, trial=False):
        base=ts[k]
        def history(q):
            if q > now+1e-11:
                raise ValueError('Future state access is forbidden.')
            if q < 0:
                return float(x2_history)
            if trial and q > base:
                return float(xs[k,1]+(q-base)/(now-base)*(state[1]-xs[k,1]))
            return float(np.interp(q,ts[:k+1],xs[:k+1,1]))
        horizon=delay(state[0])
        if horizon < 1e-14:
            p=float(state[0])
        else:
            def rhs(theta,p):
                return [spatial_rhs(float(p[0]),history(now+theta))[0]]
            sol=solve_ivp(rhs,(-horizon,0.),[state[0]],
                          method='RK45',rtol=predictor_rtol,atol=predictor_atol,
                          max_step=horizon/8.)
            if not sol.success:
                raise RuntimeError('Predictor integration failed: '+sol.message)
            p=float(sol.y[0,-1])
        p_dot,den=spatial_rhs(p,state[1])
        past=history(now-horizon)
        if example == 'oscillatory':
            # Eq. (69), selecting printed 1 or chain-rule 2 in spatial_rhs.
            u=-.5*(state[1]+.5*p)-.5*p_dot
            # Original Eqs. (67)-(68), NOT the Z2 target dynamics.
            derivative=np.array([past,u])
        else:
            kappa=p-(p-Teq)/(p+1.)
            kappa_prime=1.-(Teq+1.)/(p+1.)**2
            u=(state[0]+1.)*(state[0]-state[1])+(state[1]-kappa)-kappa_prime*p_dot
            # Original Eqs. (63)-(64), with a=-1, b=k1=k2=1.
            derivative=np.array([-(state[0]-past)*(state[0]+1.),
                                  (state[0]+1.)*(state[0]-state[1])-u])
        if not np.isfinite(np.r_[derivative,u,p]).all():
            raise FloatingPointError('Nonfinite original-plant/controller evaluation.')
        return derivative,u,p,den

    for k in range(n+1):
        f,u,p,den=evaluate(k,ts[k],xs[k])
        us[k],ps[k],dens[k]=u,p,den
        if k==n:
            break
        h=ts[k+1]-ts[k]
        trial=xs[k]+h*f
        f_trial,_,_,_=evaluate(k,ts[k+1],trial,trial=True)
        xs[k+1]=xs[k]+h*(f+f_trial)/2.
    phi=np.array([t-delay(x) for t,x in zip(ts,xs[:,0])])
    sigma=np.array([t+delay(p) for t,p in zip(ts,ps)])
    params=dict(example=example,dt=dt,t_end=t_end,factor=factor,
                x2_history=x2_history,Teq=Teq if example=='cooling' else None,
                predictor_rtol=predictor_rtol,predictor_atol=predictor_atol,
                denominator_floor=denominator_floor,
                physical_integrator='explicit Heun; linear accepted/trial state history',
                predictor_integrator='RK45, reconstructed at each physical RHS evaluation')
    return StateDelayResult(ts,xs,us,ps,dens,phi,sigma,params)


def summarize(r: StateDelayResult) -> dict:
    from scipy.signal import find_peaks
    peaks,_=find_peaks(r.U,prominence=.01)
    return dict(parameters=r.parameters,initial_control=float(r.U[0]),
                final_state=r.X[-1].tolist(),maximum_control=float(r.U.max()),
                minimum_control=float(r.U.min()),
                min_endpoint_predictor_denominator=float(r.predictor_denominator.min()),
                min_sampled_phi_increment=float(np.diff(r.phi).min()),
                peaks=[{'t':float(r.t[k]),'U':float(r.U[k])} for k in peaks],
                caveat='Own numerical run; no author code, pixel fit, or certified RoA check.')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--example',choices=['cooling','oscillatory'],default='oscillatory')
    ap.add_argument('--factor',type=int,choices=[1,2],default=1)
    ap.add_argument('--dt',type=float,default=.005)
    ap.add_argument('--t-end',type=float,default=6.)
    ap.add_argument('--history',type=float,default=None)
    ap.add_argument('--setpoint',type=float,default=.4)
    ap.add_argument('--out',type=Path,default=Path('results/state-delay-direct'))
    args=ap.parse_args()
    r=simulate(example=args.example,factor=args.factor,dt=args.dt,t_end=args.t_end,
               x2_history=args.history,Teq=args.setpoint)
    args.out.mkdir(parents=True,exist_ok=True)
    stem=f'{args.example}-factor{args.factor}-history{r.parameters["x2_history"]}-dt{args.dt}'
    np.savetxt(args.out/(stem+'.csv'),
               np.column_stack([r.t,r.X,r.U,r.P,r.predictor_denominator,r.phi,r.sigma_candidate]),
               delimiter=',',header='t,X1,X2,U,P,endpoint_denominator,phi,sigma_candidate',comments='')
    (args.out/(stem+'.json')).write_text(json.dumps(summarize(r),indent=2)+'\n')
    print(json.dumps(summarize(r),indent=2))
