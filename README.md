# Original-plant simulations for nonlinear delay-control papers

**Implementation and reproducibility project: Kenshin Kotari.**
The original models, controller designs, and theorems are attributed to the paper authors. This repository contributes numerical implementations, controlled comparisons, regression tests, and verification records. Cite the software through [CITATION.cff](CITATION.cff), separately from the original papers. Development and documentation were AI-assisted.

The default paths integrate the **original physical delayed plant**. Predictors are reconstructed from current physical state and available history; an independently propagated target trajectory never generates the physical state or applied input. An ideal reference is used only after a run for comparison.

## Project reports: equations, implementation, conditions, results

Each report identifies the paper's equation numbers, maps them to actual functions, states the experimental conditions, links the archived data, and explains both the result and what it does not establish.

| Project / experiment | Paper equations and figure | Archived outcome | Detailed report |
|---|---|---|---|
| **2016 input delay — Example 1** | Physical Eqs. **(28)–(29)**; controller **(32)**; transform **(33)–(34)**; reference **(30)–(31)**. No published Example 1 numerical figure. | At D=1, h=0.005, T=20: physical norm **0.0728144524**; maximum componentwise reconstructed-Z / ideal-reference difference **0.00435302254**. | [Equation-to-code map and full results](input-delay-2016/README.md) |
| **2012 state delay — cooling Example 1** | Physical Eqs. **(63)–(64)**; controller **(65)**; predictor **(66)**; **Fig. 3**. | At dt=0.005, T=10, assumed T_eq=0.4: history 0.2 gives **(0.399743676, 0.399951478)**; alternative 0.6 gives **(0.400096789, 0.400016819)**. | [Cooling equations, conditions, and results](state-delay-2012/README.md#cooling-results) |
| **2012 state delay — oscillatory Example 2** | Physical Eqs. **(67)–(68)**; printed **(69)–(70)** versus general **(4)–(7)** specialized with the chain rule; **Fig. 4**. | At dt=0.00125, T=6: maximum sampled control **0.089605957** for printed factor 1 versus **0.503594135** for the explicit factor-2 alternative. | [State-delay equation map and results](state-delay-2012/README.md) |

Sources for these measurements: [2016 summary.json](results/direct-dde/summary.json) and [2012 summary.csv](results/state-delay-direct/summary.csv), inspected at code snapshot `6f812dc3c37a4255bb831f95260f519fa6fb402a`. They are **our archived computations**, not numbers transcribed from the paper figures. The reports contain every stored refinement row and define the metrics. This documentation revision does not change the solvers or claim new numerical runs.

The 2016 project concerns *Stability of predictor-based feedback for nonlinear systems with distributed input delay*, Automatica 70 (2016), 195–203, DOI [10.1016/j.automatica.2016.04.011](https://doi.org/10.1016/j.automatica.2016.04.011). Its executed Example 1 is not Example 2 / Fig. 1 and does not simulate the distributed-delay extension (107)–(116).

The 2012 project concerns *Compensation of state-dependent state delay for nonlinear systems*, Systems & Control Letters 61 (2012), 849–856, DOI [10.1016/j.sysconle.2012.05.002](https://doi.org/10.1016/j.sysconle.2012.05.002). Its printed formulas, independently derived alternatives, and visual observations are kept separate.

## Run the projects

[Open the notebook in Colab](https://colab.research.google.com/github/KK1182112KK/krstic-2016-reproduction/blob/reproducibility-audit-notes/python/notebook.ipynb)

From the repository root:

```bash
pip install -r python/requirements.txt
python -m pytest python/tests/ -q
# 2016 original plant, Eq. (28)-(29), sampled feedback Eq. (32)-(34)
python python/run_direct_validation.py
python python/run_boundary_validation.py
# 2012 original plants, Eq. (63)-(64) and (67)-(68), comparison/refinement
python state-delay-2012/run_refinement.py
```

Individual state-delay runs and exact output conventions are documented in the [2012 report](state-delay-2012/README.md#7-reproduce-and-retain-outputs).

For the 2016 MATLAB implementation:

```matlab
cd matlab
run_all          % Original plant, refinement study, figures
run_all('sim')   % Direct simulations without figures
run_all('test')  % Discovered MATLAB unit tests
```

**2016 numerical contract:** only X1 and X2 are time-stepped, with RK4 and an actual issued-input buffer. Steps split at delayed command arrivals. The Eq. (32) controller is explicitly **sampled and zero-order held**, not the ideal continuous-time law. Eqs. (33)–(34) are evaluated through the exact spatial flow for that held history, up to floating-point error.

**2012 numerical contract:** original state-delay equations are stepped using explicit Heun, piecewise-linear causal state history including a provisional stage extension, and a newly solved RK45 predictor at each physical RHS evaluation. Printed factor 1 is the default; factor 2 is explicitly selected. Cooling history 0.6 and T_eq=0.4 remain hypotheses where the printed parameter statement does not supply them. Invalid predictor denominators cause an error, not clipping.

## Verification record

Evidence is associated with the **tested source snapshot**, not inferred merely from a green badge or from this documentation commit.

| Check | Recorded result | Evidence |
|---|---|---|
| Local Python suite | **45 passed**; updated notebook's **6 code cells** executed | [Verification report](docs/VERIFICATION_2026_09_07.md), [test log](results/verification-2026-09-07/python-tests.log), [source/environment manifest](results/verification-2026-09-07/manifest.json) |
| Delayed-command recording at Eq. (29) switching points | **27 mismatched output nodes to 0**, with t/X/U/Z bitwise unchanged for the archived regression | [Regression JSON](results/verification-2026-09-07/boundary-regression.json), [runner](python/run_boundary_validation.py) |
| Python GitHub Actions | **3.10, 3.11, 3.12, 3.13** jobs succeeded; notebook executed on 3.13 | [Run 34169034484](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034484) |
| MATLAB GitHub Actions | **R2026a Update 5**, **7 discovered direct-solver/boundary tests passed**, and `run_all('sim')` completed | [Run 34169034488](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034488) |

The two CI runs used a PR test-merge checkout incorporating source head `6f812dc3c37a4255bb831f95260f519fa6fb402a`. MATLAB was not executed in the local container, but was executed in CI. The MATLAB statement does not cover undiscovered legacy script tests or a MATLAB port of the 2012 examples. CI artifacts have a 30-day retention setting; compact dated local evidence is committed separately.

## Interpretation and limits

The results document numerical behavior and discrepancies in printed/example reporting; they do not establish the paper authors' actual code, a false theorem, a certified region of attraction, or misconduct. The 2016 value at T=20 is **not below 1e-6**. The 2012 oscillatory runs end at T=6, whereas Fig. 4 extends to T=10; neither a complete figure reproduction nor asymptotic convergence follows from that table alone.

The old transport-PDE functions remain opt-in comparisons (`run_all('legacy-pde')`, `run_pde_simulation`). They propagated a physical plant with an approximate delay, not just an autonomous Z trajectory. They are not the default direct-simulation path.

[Equation-numbered audit index](docs/REPRODUCIBILITY_AUDIT.md) |
[Numerical-method notes](docs/DIRECT_SIMULATION.md) |
[Reporting standard for each project](docs/REPORTING_STANDARD.md)

## License

Implementation code is covered by the existing [MIT license](LICENSE). Published papers and their figures are not redistributed. The project remains on the `reproducibility-audit-notes` review branch until its PR is merged; this documentation update does not merge it.
