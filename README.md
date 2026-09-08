# Original-plant simulations for nonlinear delay-control papers

**Implementation and reproducibility project: Kenshin Kotari.**
Original models, controller designs and theorems remain attributed to their paper authors. These repositories contribute numerical implementations, controlled comparisons, regression tests and equation-linked verification records. Cite this software through [CITATION.cff](CITATION.cff), separately from the papers. Development and documentation were AI-assisted.

## Reproduction project index

The reports below are published on their repositories' **default branches**, not only in draft PRs. Each follows source equation → implementation → conditions → measured outcome → interpretation.

| Project | Source equations emphasized | Published report |
|---|---|---|
| Bekiaris-Liberis / Krstic 2016, input delay | Physical **(28)–(29)**, controller **(32)**, transform **(33)–(34)** | [2016 report](input-delay-2016/README.md) |
| Bekiaris-Liberis / Jankovic / Krstic 2012, state delay | Cooling **(63)–(66)**, oscillatory delay **(67)–(70)** | [2012 report](state-delay-2012/README.md) |
| Ponomarev 2016, three examples | **(73)–(88)** and **(89)–(104)**, using explicitly identified arXiv-v1 numbering | [Ponomarev report](https://github.com/KK1182112KK/ponomarev-2016-reproduction/blob/master/docs/REPRODUCTION_REPORT.md) |
| Fang / Zhang 2024, inexact predictor | Predictor **(2)–(3)**, plant/controller **(35)–(40)**, Figs. 1–8 scope | [Fang report](https://github.com/KK1182112KK/fang-2024-reproduction/blob/main/docs/REPRODUCTION_REPORT.md) |

The Ponomarev and Fang reporting audits each retain nine measured numerical cases and their actual test evidence. They do **not** silently migrate those existing Euler/nearest-grid solvers to this repository's timestamp-based implementation. Method limitations and unverified stronger claims are documented individually.

## This repository: physical equations and archived outcomes

Default paths integrate the **original physical delayed plant**. Predictors are reconstructed from current physical state and available history; an independent target trajectory never generates the physical state or input. Ideal-reference comparisons occur only after a physical run.

| Experiment | Paper equations / figure | Archived numerical outcome |
|---|---|---|
| 2016 Example 1 | **(28)–(29), (32)–(34)**; reference **(30)–(31)**. No published Example 1 numerical figure. | D=1, h=0.005, T=20: physical norm **0.0728144524**; maximum componentwise Z/reference difference **0.00435302254**. |
| 2012 cooling Example 1 | **(63)–(66), Fig. 3** | dt=0.005, T=10, assumed T_eq=0.4: history 0.2 gives **(0.399743676, 0.399951478)**; alternative 0.6 gives **(0.400096789, 0.400016819)**. |
| 2012 oscillatory Example 2 | **(67)–(70)** versus general **(4)–(7)**, **Fig. 4** | dt=0.00125, T=6: maximum sampled control **0.089605957** with printed factor 1 versus **0.503594135** with explicit factor-2 alternative. |

Sources: [2016 JSON](results/direct-dde/summary.json), [2012 CSV](results/state-delay-direct/summary.csv), originally inspected at tested solver snapshot `6f812dc3c37a4255bb831f95260f519fa6fb402a`. They are our computations, not numbers transcribed from paper figures. Each detailed report supplies all stored refinement rows and definitions.

The 2016 paper is *Stability of predictor-based feedback for nonlinear systems with distributed input delay*, Automatica 70 (2016), DOI [10.1016/j.automatica.2016.04.011](https://doi.org/10.1016/j.automatica.2016.04.011). This executed Example 1 is not Example 2/Fig. 1 or the distributed-delay extension **(107)–(116)**.

The 2012 paper is *Compensation of state-dependent state delay for nonlinear systems*, Systems & Control Letters 61 (2012), DOI [10.1016/j.sysconle.2012.05.002](https://doi.org/10.1016/j.sysconle.2012.05.002). Printed formulas, derived alternatives and visual observations remain separate.

## Run this repository

[Open the default-branch notebook in Colab](https://colab.research.google.com/github/KK1182112KK/krstic-2016-reproduction/blob/master/python/notebook.ipynb)

```bash
pip install -r python/requirements.txt
python -m pytest python/tests/ -q
# 2016 original plant (28)-(29), sampled feedback (32)-(34)
python python/run_direct_validation.py
python python/run_boundary_validation.py
# 2012 original plants (63)-(64) and (67)-(68)
python state-delay-2012/run_refinement.py
```

The [2012 report](state-delay-2012/README.md#7-reproduce-and-retain-outputs) documents individual runs and output conventions. For the 2016 MATLAB implementation:

```matlab
cd matlab
run_all          % Original physical plant, refinement, figures
run_all('sim')   % Direct simulations without figures
run_all('test')  % Discovered MATLAB unit tests
```

**2016 numerical contract:** only physical X1,X2 are stepped, using RK4 and issued-input history, with steps split at delayed arrivals. Controller **(32)** is explicitly sampled and zero-order held, not the ideal continuous-time law. Transform **(33)–(34)** uses the exact spatial flow for that held history up to floating-point error.

**2012 contract:** original state-delay equations use explicit Heun, piecewise-linear history with provisional stage extension, and a newly solved RK45 predictor at each physical RHS evaluation. Printed factor 1 is default; factor 2 is explicitly selected. Cooling history 0.6 and setpoint 0.4 remain hypotheses where not supplied by the printed parameters. Invalid predictor denominators raise errors rather than being clipped.

## Tested-snapshot verification record

| Check | Recorded result | Evidence |
|---|---|---|
| Local Python suite | **45 passed**; six notebook code cells executed | [Report](docs/VERIFICATION_2026_09_07.md), [log](results/verification-2026-09-07/python-tests.log), [manifest](results/verification-2026-09-07/manifest.json) |
| Delayed-command recording at Eq. (29) switches | **27 mismatched nodes to 0**, t/X/U/Z bitwise unchanged in the recorded regression | [Regression JSON](results/verification-2026-09-07/boundary-regression.json) |
| Python CI | **3.10–3.13** jobs succeeded; notebook on 3.13 | [Run 34169034484](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034484) |
| MATLAB CI | **R2026a Update 5**, seven discovered direct/boundary tests passed and `run_all('sim')` completed | [Run 34169034488](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034488) |

These runs incorporated solver head `6f812dc3c37a4255bb831f95260f519fa6fb402a`. Their certificates apply to that recorded source, not automatically to every later commit. MATLAB was executed in CI, not locally; this does not cover undiscovered legacy scripts or a MATLAB port of the 2012 examples. CI artifacts expire after 30 days, while compact evidence remains committed.

## Interpretation and limits

The 2016 T=20 norm is **not below 1e-6**. The 2012 oscillatory runs end at T=6, while Fig. 4 extends to T=10. Neither full-figure reproduction nor asymptotic stability follows from those finite tables. Structural assumptions, source-print discrepancies and numerical implementation results are different evidence categories. No author-code access, false-theorem proof, certified RoA or misconduct claim is made.

Old transport-PDE functions remain opt-in comparisons (`run_all('legacy-pde')`, `run_pde_simulation`). They propagated a physical plant with an approximate delay, not just an autonomous target, and are not the current default.

[Equation-numbered audit index](docs/REPRODUCIBILITY_AUDIT.md) · [Numerical-method notes](docs/DIRECT_SIMULATION.md) · [Reporting standard](docs/REPORTING_STANDARD.md)

## Publication and license

PR #1 has been merged into `master`; the reports and implementations are available from the normal repository page. Implementation code uses the existing [MIT license](LICENSE). Original papers and published figures are not redistributed.
