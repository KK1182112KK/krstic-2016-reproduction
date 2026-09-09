# Original-plant simulations for nonlinear delay-control papers

**Implementation and reproducibility project: Kenshin Kotari.**
Original models, controller designs and theorems remain attributed to their paper authors. These repositories contribute numerical implementations, controlled comparisons, regression tests and equation-linked verification records. Cite this software through [CITATION.cff](CITATION.cff), separately from the papers. Development and documentation were AI-assisted.

## Reproduction project index

The reports below are published on their repositories' **default branches**, not only in draft PRs. Each follows source equation → implementation → conditions → measured outcome → interpretation.

| Project | Source equations emphasized | Published report |
|---|---|---|
| Artstein 1982, linear delayed-control reduction | Examples **(2.1)–(2.6)**, **(5.1)–(5.22)**, general reduction checks and sampled oscillator | [Artstein report](artstein-1982-reproduction/REPORT.md) |
| Bekiaris-Liberis / Jankovic / Krstic 2012, state delay | Cooling **(63)–(66)**, oscillatory delay **(67)–(70)** | [2012 report](state-delay-2012/README.md) |
| Bekiaris-Liberis / Krstic 2016, input delay | Physical **(28)–(29)**, controller **(32)**, transform **(33)–(34)** | [2016 report](input-delay-2016/README.md) |
| Bekiaris-Liberis / Krstic 2017, multi-input nonlinear predictor | Unicycle **(82)–(84)**, controller/predictors **(89)–(98)**, Figs. 3–5 | [2017 report](bekiaris-liberis-krstic-2017-reproduction/REPORT.md) |
| Zhao / Gao / Xu / Kao 2022, state-dependent two-input predictor | Predictors/clocks **(3)–(12)**, linear specialization **(24)–(31)**, traffic **(42)–(47)** | [Zhao report](zhao-2022-reproduction/REPORT.md) |
| Ponomarev 2016, three examples | **(73)–(88)** and **(89)–(104)**, using explicitly identified arXiv-v1 numbering | [Ponomarev report](https://github.com/KK1182112KK/ponomarev-2016-reproduction/blob/master/docs/REPRODUCTION_REPORT.md) |
| Fang / Zhang 2024, inexact predictor | Predictor **(2)–(3)**, plant/controller **(35)–(40)**, Figs. 1–8 scope | [Fang report](https://github.com/KK1182112KK/fang-2024-reproduction/blob/main/docs/REPRODUCTION_REPORT.md) |

The projects intentionally distinguish a source equation, an algebraic consequence, a numerical implementation and a published figure. A simulation that looks like a paper figure is not treated as a proof of a theorem, and a printed specialization discrepancy is not silently promoted to a refutation of an entire theory.

The Ponomarev and Fang reporting audits retain their measured numerical cases and actual test evidence. They do **not** silently migrate those existing Euler/nearest-grid solvers to this repository's timestamp-based implementations. Method limitations and unverified stronger claims are documented individually.

## This repository: physical equations and archived outcomes

Default paths integrate the **original physical delayed plant** whenever a physical trajectory is part of the audit. Predictors/reductions are reconstructed from current physical state and causal issued history; an independent stabilized target trajectory never generates the physical state or input. Ideal-reference comparisons occur only after, or independently of, the physical run.

| Experiment | Paper equations / figure | Archived numerical outcome |
|---|---|---|
| Artstein 1982 mixed Stieltjes audit | **(5.7)–(5.9)** | Finest tested reconstruction error **1.56906e-11**; core reduction is supported in this case. |
| Artstein 1982 printed oscillator specialization | **(2.1)–(2.3)** with audit choice kappa=2 | General-theory coefficient error **1.21548e-9** versus printed-specialization error **1.11005** at h=0.01. |
| 2012 oscillatory Example 2 | **(67)–(70)** versus general **(4)–(7)**, **Fig. 4** | dt=0.00125, T=6: maximum sampled control **0.089605957** with printed factor 1 versus **0.503594135** with explicit factor-2 alternative. |
| 2016 Example 1 | **(28)–(29), (32)–(34)**; reference **(30)–(31)** | D=1, h=0.005, T=20: physical norm **0.0728144524**; maximum componentwise Z/reference difference **0.00435302254**. |
| 2017 unicycle predictor | **(82)–(84), (89)–(98)** | P2 identity residual refines from **5.4176e-3** at h=0.04 to **3.35125e-4** at h=0.0025; compensated implementation is numerically consistent. |
| Zhao 2022 exact-trajectory diagnostic | Claimed identity after **(12)** | Literal printed second predictor differs from the exact implicit predictor by **1.08778e-5** at x0=0.2; clock-consistent alternative agrees to floating-point scale. |
| 2012 cooling Example 1 | **(63)–(66), Fig. 3** | dt=0.005, T=10, assumed T_eq=0.4: history 0.2 gives **(0.399743676, 0.399951478)**; alternative 0.6 gives **(0.400096789, 0.400016819)**. |

Sources and full refinement rows are stored in each subproject's report and machine-readable results. They are our computations, not numbers transcribed from paper figures unless a comparison is explicitly labeled as a vector-curve extraction.

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

Independent newer audits can be rerun from their own folders:

```bash
# Artstein 1982
cd artstein-1982-reproduction
pip install -r requirements.txt
python -m pytest -q test_audit.py
python audit.py --out regenerated-results
cd ..

# Bekiaris-Liberis & Krstic 2017
cd bekiaris-liberis-krstic-2017-reproduction
pip install -r requirements.txt
python -m pytest -q test_audit.py
python audit.py --out regenerated-results
# For the independent uncompensated DDE reference, run audit.py first so results/ exists:
python continuous_reference.py
python postprocess.py --results results
cd ..

# Zhao et al. 2022
cd zhao-2022-reproduction
pip install -r requirements.txt
python -m pytest -q test_audit.py
python audit.py --out regenerated-results
cd ..
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

**Artstein 1982 contract:** prescribed-input cases directly integrate the delayed original plant and reconstruct the reduction independently. Printed special-case formulas and formulas derived from the general reduction are retained as separate variants. The sampled-feedback example is explicitly zero-order held.

**2017 contract:** the original unicycle plant is advanced under delayed issued inputs. P1 and P2 are freshly reconstructed at every control update. Predictor identities are checked against future physical state only after the physical run; future physical state does not drive the controller.

**Zhao 2022 contract:** original traffic DDEs and separate exact-trajectory diagnostics are retained. The traffic `printed_product` calculation uses a disclosed closure for an otherwise future-composed term; the literal-composition diagnostic avoids that closure and is the cleaner algebraic evidence.

## Tested-snapshot verification record

| Check | Recorded result | Evidence |
|---|---|---|
| Local Python suite for 2012/2016 parent project | **45 passed**; six notebook code cells executed | [Report](docs/VERIFICATION_2026_09_07.md), [log](results/verification-2026-09-07/python-tests.log), [manifest](results/verification-2026-09-07/manifest.json) |
| Artstein 1982 audit | **16 passed** | [test log](artstein-1982-reproduction/tests.log) |
| Bekiaris-Liberis & Krstic 2017 audit | **17 passed** | [test log](bekiaris-liberis-krstic-2017-reproduction/tests.log) |
| Zhao 2022 publication | Same **14-test** source suite re-executed locally before publication | [publication provenance](zhao-2022-reproduction/PUBLICATION.md) |
| Delayed-command recording at Eq. (29) switches | **27 mismatched nodes to 0**, t/X/U/Z bitwise unchanged in the recorded regression | [Regression JSON](results/verification-2026-09-07/boundary-regression.json) |
| Python CI for prior parent snapshot | **3.10–3.13** jobs succeeded; notebook on 3.13 | [Run 34169034484](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034484) |
| MATLAB CI for prior parent snapshot | **R2026a Update 5**, seven discovered direct/boundary tests passed and `run_all('sim')` completed | [Run 34169034488](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034488) |

The older CI certificates apply to their recorded source snapshots, not automatically to later publication commits. The Artstein, 2017 and Zhao additions report local Python execution unless a later CI record explicitly says otherwise. Compact evidence remains committed even when raw trajectories are regenerated rather than stored.

## Interpretation and limits

The projects do not use journal prestige as a correctness certificate. Conversely, a printed typo, a finite numerical discrepancy, or an assumption violation in a specific example is not automatically classified as fabrication or a false theorem. Each report states the narrowest finding supported by its algebraic and numerical evidence.

The 2017 constant-delay multi-input predictor audit is an important counterexample to a blanket skeptical conclusion: **its implemented central predictor identities refine in the expected direction and the compensated published figures are closely reproduced.** The Zhao 2022 state-dependent extension has a different, explicitly documented second-predictor algebra issue. These projects are intentionally kept separate.

Old transport-PDE functions remain opt-in comparisons (`run_all('legacy-pde')`, `run_pde_simulation`). They propagated a physical plant with an approximate delay, not just an autonomous target, and are not the current default.

[Equation-numbered audit index](docs/REPRODUCIBILITY_AUDIT.md) · [Numerical-method notes](docs/DIRECT_SIMULATION.md) · [Reporting standard](docs/REPORTING_STANDARD.md)

## Publication and license

The audit subprojects are available from `master`; source papers and author-generated figures are not redistributed. Implementation code uses the existing [MIT license](LICENSE). Generated reports, executable reproduction code, machine-readable compact evidence, and local-execution provenance are published separately from the original papers.
