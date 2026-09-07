# Original-plant simulations for nonlinear delay-control papers

**Implementation and reproducibility project: Kenshin Kotari.**
This repository records numerical implementations, regression tests, and
verification evidence. The original models, controller designs, and theorems
belong to the authors of the papers cited below. Use [CITATION.cff](CITATION.cff)
to cite this software separately from those papers. Development and documentation
were AI-assisted; the archived tests identify what was actually executed.

The default simulations integrate the **original physical delayed plant**.
Predictors are reconstructed online from the current physical state and available
history. A reduced/target trajectory is never used to generate the physical
state or applied input. An ideal reference is calculated only in postprocessing.

## Latest verification

**45 Python tests passed locally**, including 12 new delayed-switch regression
cases, and all six code cells of the updated notebook executed successfully.
The 2016 delayed-input output had a floating-point boundary lookup error; it is
fixed in Python and the corresponding MATLAB code. In the archived regression,
27 incorrect output nodes became zero, while physical X, applied U, and
reconstructed Z were bitwise unchanged relative to the parent implementation.
This is a diagnostic-output fix, not a change to the control law.

[Verification report](docs/VERIFICATION_2026_09_07.md) |
[Regression metrics](results/verification-2026-09-07/boundary-regression.json) |
[Test log](results/verification-2026-09-07/python-tests.log) |
[Source/environment manifest](results/verification-2026-09-07/manifest.json)

MATLAB is source-reviewed, **not locally execution-verified**. GitHub Actions
results must be checked separately; local test logs are not CI-pass evidence.
This branch remains a draft review artifact until the PR is merged.

## 2016 input-delay example

N. Bekiaris-Liberis and M. Krstic, *Stability of predictor-based feedback for
nonlinear systems with distributed input delay*, Automatica 70 (2016), 195-203.
DOI: `10.1016/j.automatica.2016.04.011`.

The existing Example 1 uses original Eqs. (28)-(29):

```math
\dot X_1=2X_2+U(t),\qquad
\dot X_2=\frac{X_2+U(t-D)}{1+U(t-D)^2}.
```

The same scalar input acts immediately on X1 and with delay on X2. The predictor
in Eqs. (33)-(34) is a coordinate transformation, not simply the future physical
state with the eventual feedback already applied.

### Python / Colab

[Open the notebook in Colab](https://colab.research.google.com/github/KK1182112KK/krstic-2016-reproduction/blob/reproducibility-audit-notes/python/notebook.ipynb)

```bash
pip install -r python/requirements.txt
python -m pytest python/tests/ -q
python python/run_direct_validation.py
python python/run_boundary_validation.py
```

### MATLAB

```matlab
cd matlab
run_all          % Original plant, refinement study, figures
run_all('sim')   % Direct simulations without figures
run_all('test')  % MATLAB tests, including delayed-switch regressions
```

RK4 steps the original two-dimensional RHS. U(t-D) comes from a timestamped
applied-input buffer; D is not rounded to a grid index. Plant intervals split
at delayed command arrivals. There is no transport PDE on this default path.
Reported delayed commands use arrival timestamps directly, not cancellation-
prone `(t-D)` comparisons or a tolerance that could advance a command early.

**The 2016 controller is explicitly sampled and zero-order held.** This is not
an exact continuous-time implementation of the theorem. The spatial predictor
uses the exact affine flow for the actual held history, up to floating-point
error. Refine the controller period independently of the plant integrator.

For D=1, X0=[1,1], zero negative-time input, T=20:

| Sample period | max reconstructed Z minus independent ideal reference | final physical state norm |
|---|---:|---:|
| 0.02 | 1.7517e-2 | 7.5363e-2 |
| 0.01 | 8.7234e-3 | 7.3665e-2 |
| 0.005 | 4.3530e-3 | 7.2814e-2 |

These finite-horizon measurements replace earlier unsupported default-run
claims of six-digit agreement or a terminal state norm below 1e-6. They are not
a global-stability or robustness proof.

## 2012 state-delay examples

N. Bekiaris-Liberis, M. Jankovic and M. Krstic, *Compensation of state-dependent
state delay for nonlinear systems*, Systems & Control Letters 61 (2012),
849-856. DOI: `10.1016/j.sysconle.2012.05.002`.

```bash
# Printed specialization; factor 1 remains the default.
python state-delay-2012/direct_state_delay.py --factor 1 --dt 0.0025
# Explicit chain-rule-consistent alternative; physical plant unchanged.
python state-delay-2012/direct_state_delay.py --factor 2 --dt 0.0025
# Stated history, followed by an explicitly labeled alternative.
python state-delay-2012/direct_state_delay.py --example cooling --history 0.2 --setpoint 0.4 --t-end 10
python state-delay-2012/direct_state_delay.py --example cooling --history 0.6 --setpoint 0.4 --t-end 10
python state-delay-2012/run_refinement.py
```

Original Eqs. (63)-(64) or (67)-(68) are stepped with explicit Heun, causal
piecewise-linear state history (including a provisional Heun-stage extension),
and a fresh adaptive spatial predictor at each RHS evaluation. No target state
is propagated. A singular or invalid predictor raises an error instead of being
clipped. The setpoint 0.4 is an audit hypothesis, not a reported parameter.
Printed and corrected formulas, state histories, and hypotheses stay distinct.
The 2012 solver is unchanged by the delayed-input output fix.

## Methods, evidence, and attribution

[2016 metrics](results/direct-dde/summary.json) |
[2012 summary](results/state-delay-direct/summary.csv) |
[Method notes](docs/DIRECT_SIMULATION.md) |
[Combined audit](docs/REPRODUCIBILITY_AUDIT.md) |
[State-delay audit](state-delay-2012/README.md)

Earlier audit peak estimates are historical preliminary observations; use the
archived runners and measured summaries rather than treating those estimates
as independently archived results. Numerical runs do not identify the authors'
actual source code or establish misconduct. Structural assumptions and a
restricted theorem scope are not, by themselves, evidence of an invalid proof.

The old transport-PDE functions remain opt-in comparisons: `run_all('legacy-pde')`
and `run_pde_simulation`. They propagated a physical plant with an approximate
transport delay; they were not merely Z-only simulations.

## License

Implementation code is covered by the existing [MIT license](LICENSE).
Published papers and their figures are not redistributed in this repository.
