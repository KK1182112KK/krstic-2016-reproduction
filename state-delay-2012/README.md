# 2012 state-delay project: equation-to-code map and measured results

**Implementation and reproducibility project: Kenshin Kotari.**

## 1. Source, scope, and evidence

**[P12]** N. Bekiaris-Liberis, M. Jankovic, and M. Krstic, *Compensation of state-dependent state delay for nonlinear systems*, Systems & Control Letters **61** (2012), 849–856. DOI: [10.1016/j.sysconle.2012.05.002](https://doi.org/10.1016/j.sysconle.2012.05.002).

All paper equation numbers in this report refer to **[P12]**. The project covers **Example 1, Eqs. (63)–(66), Fig. 3, pp. 854–855**, and **Example 2, Eqs. (67)–(70), Fig. 4, pp. 854–855**.

Measured tables come from the committed [summary.csv](../results/state-delay-direct/summary.csv), with [environment metadata](../results/state-delay-direct/metadata.json), inspected at source snapshot `6f812dc3c37a4255bb831f95260f519fa6fb402a`. They are our computations, not author-supplied data. The environment recorded is Python 3.13.5 / NumPy 2.3.5 / SciPy 1.17.0. This documentation update changes no numerical code and reports no new simulation run.

This report supersedes the earlier preliminary peak estimates in this folder. Printed equations, our algebraic derivation, visual observations, and archived numerical results are distinguished below. No author simulation source code was obtained, and no misconduct claim is made.

## 2. Equation-to-code correspondence

Implementation: [`direct_state_delay.py`](direct_state_delay.py). The named helpers `delay`, `spatial_rhs`, and `evaluate` are nested inside `simulate`.

| Paper location | Role | Code / test | What is actually checked |
|---|---|---|---|
| Eqs. **(1)–(2)**, pp. 849–850 | Strict-feedback problem class | Scope of both examples | Not a general arbitrary nonlinear state-delay plant. |
| Eqs. **(4)–(7)**, p. 850 | Controller, spatial predictor, and predictor time derivative | `spatial_rhs`, predictor IVP in `evaluate`, controller branch | Recomputed from current/trial physical state and causal state history. |
| Eqs. **(10)–(12)**, p. 850 | Delay clock, inverse clock, feasibility condition | `phi`, `sigma_candidate`, denominator guard | Recorded diagnostics; `sigma_candidate` is not automatically certified as the inverse in (11). |
| Eq. **(20)** and target Eqs. **(21)–(22)**, pp. 850–851 | Backstepping transformation and target dynamics | [`test_continuous_target_residual_refines`](../python/tests/test_direct_state_delay.py) | A postprocessed check for the chain-rule case; (21)–(22) do not drive the physical simulation. |
| Theorem 1, Eqs. **(16)–(19)**, p. 850 | Regional stability and delay-rate guarantees | Scope/limitations only | The numerical initial conditions have not been certified against (16). |
| Eqs. **(63)–(64)**, p. 854 | Original cooling plant | `evaluate`, cooling branch | Both physical temperature states are directly stepped. The minus sign on U in (64) is retained. |
| Eq. **(65)**, p. 854; **(66)**, Box II, p. 855 | Cooling controller and predictor | Cooling `kappa`, `kappa_prime`, `spatial_rhs` | Printed history 0.2 and explicit alternative 0.6 are separate runs. |
| Eqs. **(67)–(68)**, pp. 854–855 | Original oscillatory state-delay plant | `delay`, oscillatory `evaluate` | The same physical delay 0.3 sin^2(15s) is used for both formula variants. |
| Eqs. **(69)–(70)**, p. 855 | Printed controller and predictor specialization | `factor=1` | Implemented literally; it is the default. |
| General Eqs. **(4)–(7)** applied to the delay in **(67)** | Chain-rule-consistent alternative | `factor=2` | Explicitly selected alternative, not silently attributed to printed (69)–(70). |

## 3. Common numerical method and limitations

Only the two physical plant states are time-stepped. Physical time uses explicit Heun. Each RHS stage reconstructs the spatial predictor using RK45 with rtol = **1e-8**, atol = **1e-10**, and maximum spatial step equal to the current history-window length divided by 8. Accepted state history is piecewise linear. A within-step history query at the second stage uses a provisional Euler-stage segment; this is a numerical approximation, not future measured state data.

The implementation evaluates the actual state-dependent delay rather than rounding it to a grid index. A horizon below **1e-14** is treated numerically as zero. The predictor denominator is checked at solver evaluations: a nonfinite value or a value at/below **1e-6** aborts the run instead of being clipped. This threshold is an explicit numerical guard, not the paper's feasibility certificate (12).

The result field `predictor_denominator` stores only the endpoint value at accepted physical nodes. Consequently, the reported minimum is **not** a certified infimum over every spatial predictor interval or every physical time. The code does not impose unreported positivity constraints or actuator saturation. The 2012 solver is Python; the successful MATLAB CI tests elsewhere in the repository concern the 2016 solver, not a MATLAB implementation of these 2012 examples.

<a id="cooling-results"></a>

## 4. Example 1: cooling system, Eqs. (63)–(66)

### 4.1 Paper equations and implementation

The physical equations are [P12, (63)–(64)]:

```math
\dot X_1(t)=a\left[X_1(t)-X_2\!\left(t-\frac{b}{k_1X_1(t)+k_2}\right)\right](k_1X_1(t)+k_2),\tag{63}
```
```math
\dot X_2(t)=(k_1X_1(t)+k_2)(X_1(t)-X_2(t))-U(t).\tag{64}
```

Here X1 = T_out and X2 = T_in. The controller comes from **Eq. (65)** and the predictor from **Eq. (66), Box II**. The following compact expressions are **our algebraic restatement of (65)–(66) at the stated parameters**, not additional numbered paper equations:

```math
\kappa_{eq}(P)=P-\frac{P-T_{eq}}{P+1},\qquad
\kappa_{eq}'(P)=1-\frac{T_{eq}+1}{(P+1)^2},
```
```math
q(P,v)=\frac{-(P-v)(P+1)}{1-(P-v)/(P+1)},\qquad
U=(X_1+1)(X_1-X_2)+(X_2-\kappa_{eq}(P))-\kappa_{eq}'(P)q(P,X_2).
```

The spatial predictor is anchored at the current physical X1 over the history window specified by (66). Its endpoint is recalculated at every physical RHS stage.

### 4.2 Conditions and reporting discrepancy

| Item | Paper statement / repository choice |
|---|---|
| Parameters | a = -1; b = k1 = k2 = c1 = c2 = 1, stated after (65), p. 854 |
| Physical initial state | X1(0) = 1 |
| Printed initial history | X2(theta) = **0.2** on [-0.5, 0], stated after (65) |
| Alternative history | X2(theta) = **0.6**; an explicit audit hypothesis, not the printed value |
| Setpoint | **T_eq = 0.4**, an explicit repository hypothesis; (65) uses T_eq but the numerical-parameter sentence omits its value |
| Physical steps / run length | dt = 0.01 and 0.005; **T = 10**, chosen for this audit |

**Visual observation, not digitized data:** Fig. 3 on p. 854 appears to start T_in near 0.6 and approach 0.4. This differs from the printed history 0.2. The plot alone does not identify the author's source code. In particular, an ODE state cannot be treated as making an unreported instantaneous jump from 0.2 to 0.6.

### 4.3 Archived numerical results

Data: [summary.csv](../results/state-delay-direct/summary.csv), rows with `example=cooling`. Values are rounded; `factor` has no effect in the cooling branch.

| Initial X2 history | dt | U(0+) | X1(10) | X2(10) | Minimum sampled endpoint denominator |
|---:|---:|---:|---:|---:|---:|
| 0.2 (printed) | 0.01 | 1.535321435 | 0.399743656 | 0.399951476 | 0.824643499 |
| 0.2 (printed) | 0.005 | 1.535321435 | 0.399743676 | 0.399951478 | 0.824643499 |
| 0.6 (alternative) | 0.01 | 0.996662866 | 0.400096794 | 0.400016819 | 0.920321839 |
| 0.6 (alternative) | 0.005 | 0.996662866 | 0.400096789 | 0.400016819 | 0.920321839 |

**Result:** both initial-history choices reach temperatures close to the assumed 0.4 setpoint in these runs, but their initial states and initial control values differ. The two tested steps produce close terminal values. The alternative 0.6 history is more consistent with the visible starting temperature and roughly unit initial input in Fig. 3; this is a qualitative comparison only.

**Not established:** exact reproduction of Fig. 3, a verified value of the author's T_eq, a setpoint sweep, or a proof that the author used history 0.6. The archived runner does not supply an open-loop comparison for the dashed curves in Fig. 3. Earlier conversational open-loop equilibrium estimates are therefore not treated as archived results here. Positivity and the physical inequalities discussed below (64) have not been independently certified.

## 5. Example 2: oscillatory delay, Eqs. (67)–(70)

### 5.1 Keep the printed and derived formulas separate

The original plant is [P12, (67)–(68)]:

```math
\dot s(t)=v\!\left(t-r_1\sin^2(\omega s(t))\right),\tag{67}
```
```math
\dot v(t)=a(t).\tag{68}
```

Define d_m(P,v) = 1 - m r1 omega sin(omega P) cos(omega P) v, where **m is a repository comparison parameter**. Both variants use the physical delay in (67) unchanged.

**Printed m = 1:** Eqs. (69)–(70) give

```math
a(t)=-c_2(v(t)+c_1P(t))-c_1\frac{v(t)}{d_1(P(t),v(t))},\tag{69}
```
```math
P(\theta)=s(t)+\int_{t-r_1\sin^2(\omega s(t))}^{\theta}
\frac{v(\eta)}{d_1(P(\eta),v(\eta))}\,d\eta.\tag{70}
```

The shorthand d1 and dummy variable eta are only notational restatements of the printed expressions. Their denominator does **not** contain the factor 2.

**Derived m = 2:** directly differentiating the delay specified in (67) gives

```math
D'(s)=2r_1\omega\sin(\omega s)\cos(\omega s).
```

Substituting this derivative into general **Eqs. (4)–(7)** produces d2, not d1. Replacing d1 by d2 in the two expressions above is the explicitly labeled chain-rule-consistent alternative. Thus there is an algebraic discrepancy between the general design and its printed specialization. This observation does not, by itself, invalidate Theorem 1 or identify which formula the authors executed.

### 5.2 Conditions

The parameters following (68), on p. 855, are r1 = **0.3**, omega = **15**, c1 = c2 = **0.5**, s(0) = **1**, and v(theta) = **0.1** over the initial delay interval. These values are used for both variants.

The archived audit uses **T = 6** and dt = **0.005, 0.0025, 0.00125**. Fig. 4 extends to **T = 10**. Our six-second study therefore is not a full-horizon reproduction of that figure. The stored `sigma_candidate` is t + D(P), motivated by Eq. (6); for m = 1 it is not asserted to equal the inverse clock in Eq. (11).

### 5.3 Archived numerical results

Data: [summary.csv](../results/state-delay-direct/summary.csv), rows with `example=oscillatory`. Maxima/minima are over accepted time nodes, not certified continuous extrema.

| Formula | dt | Maximum sampled a(t) | Minimum sampled endpoint d_m | s(6) | v(6) |
|---|---:|---:|---:|---:|---:|
| m = 1, printed (69)–(70) | 0.005 | 0.089566450 | 0.571077176 | 0.231453135 | -0.086811499 |
| m = 1, printed (69)–(70) | 0.0025 | 0.089605703 | 0.571076244 | 0.231451995 | -0.086811237 |
| m = 1, printed (69)–(70) | 0.00125 | 0.089605957 | 0.571075968 | 0.231451723 | -0.086811176 |
| m = 2, derived alternative | 0.005 | 0.501912765 | 0.156064618 | 0.245266084 | -0.089884030 |
| m = 2, derived alternative | 0.0025 | 0.502795829 | 0.155853731 | 0.245259826 | -0.089882990 |
| m = 2, derived alternative | 0.00125 | 0.503594135 | 0.155149816 | 0.245259228 | -0.089882847 |

At startup a(0+) = **-0.344254676** for m = 1 and **-0.337660685** for m = 2. The controller/predictor formula choice already changes the initial command.

**Result:** the difference in positive control maxima persists across these three steps: roughly **0.090** for the printed specialization versus **0.504** for the derived alternative. Fig. 4 visibly contains a positive peak near 0.5, so the latter is qualitatively more consistent with that feature. No pixel-based error norm or full-curve fit was computed. The corrected-case peak and denominator minimum still shift with refinement; extra displayed digits are not a rigorous accuracy certificate.

Both runs finish at nonzero s(6), v(6). Their finite responses cannot establish global stability or validate the paper's regional theorem for these specific initial histories. For m = 1, d1 is not the true chain-rule clock denominator associated with (67); its positive minimum is therefore **not** a certificate of Eq. (12).

The committed CSV does not contain the times and magnitudes of every local peak. `summarize` can output sampled local peaks using prominence 0.01, but earlier estimates such as “0.51, 0.33, 0.12” are not substituted for the archived table above.

## 6. Theorem-level assessment and checks

The paper's construction uses predictor Eqs. **(5)–(7)**, clocks **(10)–(11)**, feasibility **(12)**, and the backstepping transform **(20)** to obtain target Eqs. **(21)–(22)**. Assumption 3 posits an ISS nominal feedback and includes the bound **(15)**. Theorem 1 states the small-initial-condition requirement **(16)** and conclusions **(17)–(19)**. Lemmas 7–8, particularly **(57)–(62)**, address feasibility and the attraction-region estimate.

These are the paper's conditional claims, not conclusions proved by our plots. No certified numerical value of xi_RoA(c) or check of (16) is supplied by this project. The earlier discussion about making the first-exit/continuation argument explicit is an **unresolved proof-review question**, not an established circular-proof defect. Restricted scope is not itself evidence that the theorem is wrong.

[`test_direct_state_delay.py`](../python/tests/test_direct_state_delay.py) checks, among other things, the following consequences rather than using a target to generate the plant:

- For m = 2 and constant initial v, the initial predictor obeys the clock relation from (6)–(7).
- Before the first feedback arrival, (67) gives s(t) = 1 + 0.1t; the short-time numerical trajectory is checked against this.
- With kappa(P) = -0.5P, (20) gives z = v + 0.5P; its deviation from the exponential implied by (22) decreases under short-run step refinement.

These tests do not certify every point of the long-run history or all initial conditions. Python CI at the cited snapshot passed on 3.10–3.13; the [notebook run on 3.13](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/runs/34169034484) exercised both formula variants and both cooling histories. A test-suite pass is not a separate theorem proof.

## 7. Reproduce and retain outputs

Run from the repository root:

```bash
pip install -r python/requirements.txt
python -m pytest python/tests/ -q
python state-delay-2012/run_refinement.py
# Individual runs, including full trajectory CSV and JSON summary:
python state-delay-2012/direct_state_delay.py --factor 1 --dt 0.00125 --t-end 6
python state-delay-2012/direct_state_delay.py --factor 2 --dt 0.00125 --t-end 6
python state-delay-2012/direct_state_delay.py --example cooling --history 0.2 --setpoint 0.4 --dt 0.005 --t-end 10
python state-delay-2012/direct_state_delay.py --example cooling --history 0.6 --setpoint 0.4 --dt 0.005 --t-end 10
```

`run_refinement.py` produces a fresh JSON summary for all comparisons and oscillatory trajectory CSVs. Use the individual cooling commands to retain their full trajectories. The committed compact CSV is the source of the tables above; regeneration produces new files and does not automatically certify equality to it.

Original theory: cite [P12]. Software/reproduction project: cite [CITATION.cff](../CITATION.cff). Reporting convention: [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md).
