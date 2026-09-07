# Original-plant simulations for nonlinear delay-control papers

The default simulations integrate the **original physical delayed plant**. The
predictor is reconstructed online from the current physical state and available
history. A reduced/target-system trajectory is **never** used to generate the
plant state or the applied control.

## Run the 2016 input-delay example

Source: N. Bekiaris-Liberis and M. Krstic, *Stability of predictor-based feedback
for nonlinear systems with distributed input delay*, Automatica 70 (2016),
195-203. DOI: `10.1016/j.automatica.2016.04.011`.

The existing Example 1 uses the original Eqs. (28)-(29):

```math
\dot X_1=2X_2+U(t),\qquad
\dot X_2=\frac{X_2+U(t-D)}{1+U(t-D)^2}.
```

The same scalar input acts immediately on X1 and with delay on X2. The predictor
in Eqs. (33)-(34) is a coordinate transformation, not simply the future physical
state with the eventual feedback already applied.

### Python / Colab

[Open the direct-simulation notebook in Colab](https://colab.research.google.com/github/KK1182112KK/krstic-2016-reproduction/blob/reproducibility-audit-notes/python/notebook.ipynb)

From a checkout, run:

```bash
pip install -r python/requirements.txt
python python/run_direct_validation.py
python -m pytest python/tests/test_direct_dde.py python/tests/test_direct_state_delay.py -q
```

### MATLAB

```matlab
cd matlab
run_all          % Original plant, refinement study, figures
run_all('sim')   % Same direct simulations, without figures
run_all('test')  % MATLAB tests
```

**Numerical implementation:** RK4 steps the original two-dimensional physical
RHS. U(t-D) is read from an actual timestamped input buffer. D is not rounded to
a grid index; steps are split at delayed input switches. Each controller sample
reconstructs Z from X and the past applied input. There is no transport PDE in
this path.

**Important:** the 2016 controller is explicitly **sampled and zero-order held**.
This is not an exact continuous-time implementation of the theorem. The sample
period is recorded, and the runner compares periods 0.02, 0.01, and 0.005.
The spatial predictor is integrated exactly for this piecewise-constant input
history, up to floating-point error. No new plant-structure assumption is added.

## Run the 2012 state-delay examples

Source: N. Bekiaris-Liberis, M. Jankovic and M. Krstic, *Compensation of
state-dependent state delay for nonlinear systems*, Systems & Control Letters
61 (2012), 849-856. DOI: `10.1016/j.sysconle.2012.05.002`.

```bash
# Literal printed Eq. (69)-(70) specialization: factor 1 (the default)
python state-delay-2012/direct_state_delay.py --factor 1 --dt 0.0025
# Chain-rule-consistent alternative, explicitly selected; plant unchanged
python state-delay-2012/direct_state_delay.py --factor 2 --dt 0.0025
# Cooling: use the stated history first, and label the alternative as a hypothesis
python state-delay-2012/direct_state_delay.py --example cooling --history 0.2 --setpoint 0.4 --t-end 10
python state-delay-2012/direct_state_delay.py --example cooling --history 0.6 --setpoint 0.4 --t-end 10
# Both factor cases / both histories and time-step refinement
python state-delay-2012/run_refinement.py
```

These runs use original Eqs. (63)-(64) or (67)-(68), explicit Heun in physical
time, a causal piecewise-linear state-history representation (with a provisional
Heun-stage extension), and a fresh adaptive spatial predictor solve at every
RHS evaluation. No target-system state is propagated. A singular/invalid
predictor raises an error; there is no undocumented denominator clipping,
actuator saturation, parameter fitting, or replacement by a stable target ODE.
The setpoint 0.4 is an explicit audit hypothesis, **not** a value supplied by the
paper's parameter sentence. A finite successful run does not certify its RoA.

## Verified results and limits

The new Python tests pass locally: **27 tests**, Python 3.13.5, NumPy 2.3.5,
SciPy 1.17.0. MATLAB code is provided but was **not executed** in this local
Python environment. Existing CI workflows target `main`, whereas this PR targets
`master`; no CI pass is claimed. Run the MATLAB tests explicitly before relying
on that implementation.

For the 2016 direct run (D=1, X0=[1,1], zero negative-time input, T=20):

| Sample period | max reconstructed Z minus independent ideal reference | final physical state norm |
|---|---:|---:|
| 0.02 | 1.7517e-2 | 7.5363e-2 |
| 0.01 | 8.7234e-3 | 7.3665e-2 |
| 0.005 | 4.3530e-3 | 7.2814e-2 |

The reference is calculated **after** the direct physical simulation and is
never available to its controller. These finite-horizon results replace the
previous README's unverified six-digit-agreement / 1e-6 terminal-convergence
claims for the default run. Refinement evidence is not an asymptotic-stability
proof or a robustness certificate.

[2016 run metadata and metrics](results/direct-dde/summary.json) |
[2012 direct-run summary](results/state-delay-direct/summary.csv) |
[Method and migration notes](docs/DIRECT_SIMULATION.md)

The old transport-PDE functions remain for comparison and are explicitly opt-in:
`run_all('legacy-pde')` in MATLAB; `run_pde_simulation` in Python. They were not
Z-only simulations: they propagated the physical plant with an approximate
transport delay. They are no longer the default notebook/run_all path.

## Audit notes

[Combined paper audit](docs/REPRODUCIBILITY_AUDIT.md) |
[State-delay paper audit](state-delay-2012/README.md)

The algebraic/reporting observations, the original theory's assumptions, and
our numerical results are different kinds of evidence. Earlier preliminary
peak values should not be treated as archived measurements; use the current
scripts and generated summaries. No allegation of misconduct is made.

## License

Original implementation code is covered by the repository's [MIT license](LICENSE).
The cited papers and their published figures are not redistributed here.
