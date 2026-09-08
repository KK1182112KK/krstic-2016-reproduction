"""Archive our runs of both printed/corrected cases; never claim author-code access."""
import json
import platform
from pathlib import Path
import numpy as np
import scipy
from direct_state_delay import simulate, summarize

if __name__=='__main__':
    out=Path(__file__).resolve().parents[1]/'results/state-delay-direct'
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for factor in (1,2):
        for dt in (.005,.0025,.00125):
            r=simulate(factor=factor,dt=dt,t_end=6.)
            row=summarize(r); rows.append(row)
            np.savetxt(out/f'oscillatory-factor{factor}-dt{dt}.csv',
                       np.column_stack([r.t,r.X,r.U,r.P,r.predictor_denominator,r.phi,r.sigma_candidate]),
                       delimiter=',',header='t,X1,X2,U,P,endpoint_denominator,phi,sigma_candidate',comments='')
            print(f'factor={factor}, dt={dt}, max U={r.U.max():.9f}',flush=True)
    for history in (.2,.6):
        for dt in (.01,.005):
            r=simulate(example='cooling',x2_history=history,Teq=.4,dt=dt,t_end=10.)
            rows.append(summarize(r))
            print(f'cooling history={history}, dt={dt}, U0={r.U[0]:.9f}',flush=True)
    data=dict(paper_doi='10.1016/j.sysconle.2012.05.002',python=platform.python_version(),
              numpy=np.__version__,scipy=scipy.__version__,runs=rows,
              limitations=['Own original-DDE computations; no author simulation code available.',
                           'Setpoint .4 is an explicit audit hypothesis, not a documented parameter.',
                           'No automatic fit to published plots; no certified RoA or robustness proof.',
                           'Endpoint denominator minima are sampled diagnostics, not certified infima.'])
    (out/'summary.json').write_text(json.dumps(data,indent=2)+'\n')
