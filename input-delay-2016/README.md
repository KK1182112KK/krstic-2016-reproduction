# 2016 input-delay project: equation-to-code map and measured results

**Implementation and reproducibility project: Kenshin Kotari.**

## 1. Source, scope, and evidence

**[P16]** N. Bekiaris-Liberis and M. Krstic, *Stability of predictor-based feedback for nonlinear systems with distributed input delay*, Automatica **70** (2016), 195–203. DOI: [10.1016/j.automatica.2016.04.011](https://doi.org/10.1016/j.automatica.2016.04.011).

Equation numbers below refer to **[P16]**, not to this repository. The executed project is **Example 1, Eqs. (28)–(34), pp. 197–198**. It is not the different Example 2 plotted in Fig. 1 on p. 199, and it is not the distributed-delay extension in Eqs. (107)–(116).

The results below are transcribed from the committed [2016 summary](../results/direct-dde/summary.json), inspected at source snapshot `6f812dc3c37a4255bb831f95260f519fa6fb402a`. The summary records Python 3.13.5, NumPy 2.3.5, and SciPy 1.17.0. It is an archived local-run record, not data supplied by the paper authors. This documentation update does not change the solver or claim a new simulation run.

## 2. What the paper says and what the code executes

| Paper location | Mathematical role | Implementation / verification | Outcome or scope |
|---|---|---|---|
| Eqs. **(28)–(29)**, p. 197 | Original physical delayed plant | [`plant_rhs`, `plant_step`, `simulate`](../python/src/direct_dde.py); MATLAB [`physical_rhs`, `run_original_dde`](../matlab/src/run_original_dde.m) | The physical states X1 and X2 are advanced directly; the delayed input remains in the RHS. |
| Eq. **(32)**, p. 197 | Feedback U = -Z1 - 2 Z2 | `simulate` / `run_original_dde` | Evaluated at controller samples and zero-order held. This is a stated numerical implementation change, not the ideal continuous-time law. |
| Eqs. **(33)–(34)**, p. 198 | History-dependent coordinate transform X to Z | `predictor_from_history`; MATLAB `history_predictor` | Reconstructed from physical X and issued-input history at each sample. |
| Eqs. **(79)–(82)**, pp. 199–200 | Type II spatial-predictor representation | Spatial IVP used inside the preceding functions | An equivalent way of evaluating (33)–(34), not an independently propagated target trajectory. |
| Eqs. **(30)–(31)** with **(32)**, p. 197 | Ideal transformed closed loop | [`target` inside `run_direct_validation.py`](../python/run_direct_validation.py) | Solved only after the physical run; used as an independent reference, never to generate X or U. |
| Eqs. **(30)–(31)** | Transformation identity under the applied input | `identity_residual` | A postprocessed trapezoidal integral-defect diagnostic; results reported below. |
| Theorem 1, Eqs. **(15)–(18)**, p. 197 | Conditional stability transfer and history norm | Theory context only | Finite sampled runs do not establish the KL bound in (17), and the reported terminal X norm is not Gamma in (18). |
| Eqs. **(64)–(71)** / Fig. 1, p. 199 | Different Example 2 | [Combined audit](../docs/REPRODUCIBILITY_AUDIT.md) | Startup consistency analyzed; no archived executable Example 2 run is certified by this project's metrics. |

### Physical equations retained

The simulated equations are exactly the physical RHS of [P16, Eqs. (28)–(29)]:

```math
\dot X_1(t)=2X_2(t)+U(t),\tag{28}
```
```math
\dot X_2(t)=\frac{X_2(t)+U(t-D)}{1+U(t-D)^2}.\tag{29}
```

The same scalar U enters X1 immediately and X2 after D. The code does not describe this plant as having only a delayed input channel.

For clarity, the following is a **derived IVP restatement** of the transform in [P16, Eqs. (33)–(34), also see (79)–(82)]:

```math
\frac{dp_1}{d\xi}=2p_2,\qquad
\frac{dp_2}{d\xi}=\frac{p_2+U(t+\xi-D)}{1+U(t+\xi-D)^2},
\qquad p(0)=X(t),\qquad Z(t)=p(D).
```

Only this controller calculation uses p. The physical simulation does not integrate the delay-free equations (30)–(31) instead of (28)–(29). The exact affine spatial flow is evaluated on each held-input interval, up to floating-point error.

## 3. Reproduction conditions

These are **repository-selected conditions** for Example 1, not claimed to be parameters of a published Example 1 simulation figure.

| Setting | Value / convention |
|---|---|
| Plant / controller | [P16, (28)–(29)] / sampled evaluation of [P16, (32)–(34)] |
| Delay | D = 1; not rounded to an integer number of samples |
| Physical initial state | X1(0) = X2(0) = 1 |
| Input history | U(theta) = 0 for theta < 0; U(0+) is computed by (32) |
| End time | T = 20 |
| Controller sample periods | h = 0.02, 0.01, 0.005 |
| Applied input | U(t) = U(t_k) on [t_k, t_(k+1)); no clipping or saturation |
| Physical integration | RK4 on (28)–(29), splitting each step at delayed command arrivals |
| Predictor | Recomputed from current X and actual issued-input history |
| Independent plant check | `plant_method='exact-held'`: analytic integration of the same original RHS for the same held inputs |
| Independent ideal reference | Eqs. (30)–(32), `solve_ivp`, rtol = 1e-11, atol = 1e-13, initialized at the same reconstructed Z(0) |

The zero-history specialization of (33)–(34) gives, by direct calculation,

```math
Z_1(0)=2e-1,\qquad Z_2(0)=e,\qquad U(0^+)=1-4e\approx-9.873127314.
```

Thus this run deliberately has a startup input jump. It is not presented as satisfying the continuous initial-history compatibility condition in the unnumbered **Solutions** paragraph on p. 196 and Eq. (8). That observation concerns initialization/solution class, not fabrication or failure of the theorem.

## 4. Measured results

### 4.1 Physical state and comparison with Eqs. (30)–(32)

Data: [summary.json, `runs`](../results/direct-dde/summary.json). Values are rounded for display.

| h | X1(20) | X2(20) | Euclidean norm of X(20) | Maximum componentwise Z-reference difference |
|---:|---:|---:|---:|---:|
| 0.02 | -0.0599006172 | 0.0457332383 | 0.0753632073 | 0.0175168477 |
| 0.01 | -0.0581974391 | 0.0451615191 | 0.0736648134 | 0.00872341165 |
| 0.005 | -0.0573420643 | 0.0448757411 | 0.0728144524 | 0.00435302254 |

**Definition of the last column:** maximum over sampled times and the two components of the absolute difference between reconstructed Z and the independently computed ideal solution of (30)–(32). This is not a Euclidean norm, a paper-reported error, or a comparison to digitized figure pixels.

**Interpretation:** the Z-reference discrepancy approximately halves when the controller period halves in this experiment. This supports consistency of this sampled implementation with the ideal transformed trajectory as the period is refined, over this tested range. It is not a proof of a general convergence order or a sampled-data stability theorem. At T = 20 the physical state is small but is **not below 1e-6**. This corrects an earlier repository claim; it does not establish instability.

The maximum sampled absolute input was **9.873127314** for all three runs. This is a measurement for the selected history/initial state, not a general input bound from Theorem 1.

### 4.2 Identity and original-RHS integration checks

Data: [summary.json](../results/direct-dde/summary.json), fields `max_identity_integral_defect_per_time` and `max_RK4_vs_exact_held_plant`.

| h | Maximum normalized identity defect | Maximum componentwise X difference: RK4 vs exact held-plant flow |
|---:|---:|---:|
| 0.02 | 1.08184358e-5 | 1.98615620e-8 |
| 0.01 | 2.70547863e-6 | 1.25166988e-9 |
| 0.005 | 6.76477173e-7 | 7.85547183e-11 |

For F in [P16, (30)–(31)], the first metric is the maximum absolute component of the **repository-defined** quantity

```math
r_k=\frac{Z_{k+1}-Z_k}{t_{k+1}-t_k}
-\frac{F(Z_k,U_k)+F(Z_{k+1},U_k)}{2}.
```

Both endpoint RHS values use the held U_k. The trapezoidal approximation contributes its own error. This diagnostic is not a paper theorem or a rigorous error bound. The second metric checks two integrations of the **same original physical plant**, not original X versus a reconstructed target X.

### 4.3 Delayed-input recording correction tied to Eq. (29)

A repository bug used cancellation-prone `t-D` subtraction to record the right-continuous delayed command at a switching time. The correction compares physical time directly with issued-command arrival times. It does not alter (29), (32), or the integration/predictor algorithms.

For D = 1, h = 0.01, T = 3, the archived regression changed **27 mismatched recorded nodes to 0**; t, X, U, and Z were bitwise unchanged against the baseline implementation. This result is limited to the archived comparison, not all possible floating-point conditions.

Evidence: [regression JSON](../results/verification-2026-09-07/boundary-regression.json), [Python regression](../python/tests/test_delay_switch_boundaries.py), [MATLAB regression](../matlab/tests/test_delay_switch_boundaries.m), and [verification report](../docs/VERIFICATION_2026_09_07.md).

## 5. What is and is not established

The executed evidence supports the original-RHS implementation, causal input-history handling, the stated regression correction, and the observed refinement behavior. Tests also check X2(t) = exp(t) before the first delayed control arrives, a direct consequence of (29) for zero prehistory.

The paper's Theorem 1 assumes Assumptions 1–3, including the separation in Eq. (10), completeness, and the feedback properties in Eqs. (15)–(16). They define the theorem's scope; they are not by themselves evidence of a circular proof. This project does not independently certify the whole theorem, the KL bound (17), robustness, all delays/initial histories, or the distributed-delay extension (107)–(116).

**Example 1 has no published numerical figure to match.** Do not label these results “Fig. 1 reproduced”: that figure belongs to Example 2, (64)–(71). Earlier conversational Example 2 peak estimates are not the archived measurements in this report.

## 6. Run and inspect

From the repository root:

```bash
pip install -r python/requirements.txt
python python/run_direct_validation.py
python python/run_boundary_validation.py
python -m pytest python/tests/ -q
```

`run_direct_validation.py` writes `results/direct-dde/trajectory-dt*.csv` and a fresh `summary.json`. The committed summary is a dated record; regenerated files have the current environment. For interactive execution, use the [notebook](../python/notebook.ipynb).

```matlab
cd matlab
run_all('sim')
run_all('test')
```

At the source snapshot above, [Python CI run 34169034484](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034484) succeeded on Python 3.10–3.13; the notebook ran on 3.13. [MATLAB CI run 34169034488](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034488) ran R2026a Update 5, passed the **7 discovered direct-solver/boundary tests**, and completed `run_all('sim')`. Undiscovered legacy script tests and pointwise cross-language agreement are not covered by that statement.

Original mathematics: cite [P16]. Implementation/reproduction project: cite [CITATION.cff](../CITATION.cff). See the [reporting standard](../docs/REPORTING_STANDARD.md) for how subsequent results should be documented.
