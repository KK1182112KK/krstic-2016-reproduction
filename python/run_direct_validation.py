"""Run and archive original-plant tests/refinement. From repository root:
python python/run_direct_validation.py --out results/direct-dde
"""
import argparse
import json
import platform
import sys
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from direct_dde import simulate, identity_residual


def main(out: Path):
    out.mkdir(parents=True,exist_ok=True)
    rows=[]; prev=None
    for dt in (.02,.01,.005):
        r=simulate(sample_dt=dt,t_end=20.)
        # Entire physical trajectory is already finished before this reference.
        def target(t,z):
            u=-z[0]-2*z[1]
            return [2*z[1]+u,(z[1]+u)/(1+u*u)]
        ref=solve_ivp(target,(0.,20.),r.Z[0],t_eval=r.t,rtol=1e-11,atol=1e-13)
        if not ref.success:
            raise RuntimeError(ref.message)
        exact=simulate(sample_dt=dt,t_end=20.,plant_method='exact-held')
        change=None
        if prev is not None:
            fine=np.column_stack([np.interp(prev.t,r.t,r.X[:,j]) for j in range(2)])
            change=float(np.max(np.abs(fine-prev.X)))
        rows.append(dict(sample_dt=dt,final_X=r.X[-1].tolist(),
                         final_X_norm=float(np.linalg.norm(r.X[-1])),
                         max_abs_U=float(np.max(np.abs(r.U))),
                         max_Z_vs_ideal_reference=float(np.max(np.abs(r.Z-ref.y.T))),
                         max_identity_integral_defect_per_time=float(np.max(np.abs(identity_residual(r)))),
                         max_RK4_vs_exact_held_plant=float(np.max(np.abs(r.X-exact.X))),
                         max_X_change_from_coarser=change))
        np.savetxt(out/f'trajectory-dt{dt}.csv',
                   np.column_stack([r.t,r.X,r.U,r.Z,r.U_delayed]),delimiter=',',
                   header='t,X1,X2,U,Z1,Z2,U_delayed',comments='')
        prev=r
    summary=dict(paper_doi='10.1016/j.automatica.2016.04.011',example=1,
                 physical_equations='28-29',controller_equations='32-34',
                 D=1.,X0=[1.,1.],negative_time_input=0.,t_end=20.,
                 controller='sampled, zero-order hold; not exact continuous-time',
                 plant='RK4 original physical RHS, split at delayed input switches',
                 predictor='reconstructed exact affine flow for the actual ZOH history',
                 reference='independent postprocessing only, never used by controller',
                 python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                 runs=rows,matlab_execution='not executed in the local Python environment')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=Path('results/direct-dde'))
    main(ap.parse_args().out)
