# Reproducibility Audit — State-Dependent State Delay (2012)

This folder records an independent audit of:

> N. Bekiaris-Liberis, M. Jankovic, and M. Krstic,  
> **“Compensation of state-dependent state delay for nonlinear systems,”**  
> *Systems & Control Letters*, vol. 61, pp. 849–856, 2012.  
> DOI: `10.1016/j.sysconle.2012.05.002`

The purpose of this folder is **reproducibility and mathematical consistency checking**. It is not an allegation of misconduct. Findings are separated into (i) theorem-level mathematics, (ii) printed-example algebra, and (iii) numerical-reporting discrepancies.

---

## 1. Plant class and scope

The paper studies the strict-feedback architecture

```math
\dot X_1(t)=f_1\!\left(t,X_1(t),X_2\bigl(t-D(X_1(t))\bigr)\right),
```

```math
\dot X_2(t)=f_2(t,X_1(t),X_2(t))+U(t).
```

This is a structured subclass of nonlinear state-delay systems rather than a general nonlinear state-delay plant. In particular:

- the delay acts on the virtual-input state `X_2`;
- the delay is a function of the current `X_1` only;
- the actual control enters through a scalar integrator-like channel;
- the nominal `X_1` subsystem is assumed to admit an ISS-stabilizing feedback `κ`.

The main theorem is regional because the predictor requires a delay-rate feasibility condition.

---

## 2. Core predictor identity

The paper defines

```math
\phi(t)=t-D(X_1(t))
```

and uses its inverse `σ=φ^{-1}`. The feasibility condition is

```math
\nabla D(P_1(\theta))
 f_1(\sigma(\theta),P_1(\theta),X_2(\theta)) < c < 1.
```

Under this condition,

```math
\phi'(t)>1-c>0,
```

so the inverse time map exists. The predictor satisfies

```math
P_1(t)=X_1(\sigma(t))
```

and therefore

```math
\dot P_1(t)=
\frac{f_1(\sigma(t),P_1(t),X_2(t))}
{1-\nabla D(P_1(t))f_1(\sigma(t),P_1(t),X_2(t))}.
```

The backstepping variable

```math
Z_2(\theta)=X_2(\theta)-\kappa(\sigma(\theta),P_1(\theta))
```

is designed so that the target dynamics contain

```math
\dot Z_2=-c_2Z_2.
```

### Current assessment

The **general predictor/backstepping derivation appears structurally coherent** under the stated assumptions. The main concerns identified below are not, at present, evidence that the core theorem is false.

---

## 3. Example 1 — cooling system: reported initial condition vs. Fig. 3

The paper states the simulation parameters

```math
a=-1,\qquad c_1=c_2=b=k_1=k_2=1,
```

with

```math
X_1(0)=1,
\qquad
X_2(\theta)=0.2
```

on the initial delay interval.

However, in Fig. 3 the plotted `T_in=X_2` trajectory appears to start near **0.6**, not 0.2.

A preliminary numerical reproduction indicated that an initial history near

```math
X_2(\theta)=0.6
```

is substantially more consistent with the published plot than the stated value 0.2.

The controller also contains the setpoint `T_eq`, but the numerical value of `T_eq` is not explicitly included in the parameter sentence. The plotted controlled trajectories converge near 0.4, suggesting

```math
T_{eq}\approx0.4.
```

### Status

**Potential reporting discrepancy.** The conservative explanation is a typographical error and/or omitted simulation parameter. This should be treated as preliminary until the archived reproduction script and convergence checks are committed.

---

## 4. Example 2 — algebraic factor-of-two discrepancy

The Example 2 delay is

```math
D(s)=r_1\sin^2(\omega s).
```

Hence, by direct differentiation,

```math
D'(s)=2r_1\omega\sin(\omega s)\cos(\omega s).
```

The **general** predictor formula in the paper uses the denominator

```math
1-\nabla D(P_1)f_1.
```

For Example 2, since `f_1=v`, this specializes to

```math
1-
2r_1\omega\sin(\omega P_1)\cos(\omega P_1)v.
```

However, the printed specialized controller/predictor equations (69)–(70) use

```math
1-
r_1\omega\sin(\omega P_1)\cos(\omega P_1)v,
```

which is missing the factor **2**.

### Mathematical implication

This is a direct algebraic inconsistency between the paper's general formula and its Example 2 specialization.

### Preliminary numerical observation

Using the paper's stated parameters

```math
r_1=0.3,\qquad \omega=15,
\qquad c_1=c_2=0.5,
```

```math
s(0)=1,
\qquad v(\theta)=0.1,
```

preliminary numerical checks found:

- the printed factor-1 specialization does **not** reproduce the large control spikes shown in Fig. 4;
- the mathematically corrected factor-2 specialization produces spikes much closer to the plotted locations and magnitudes;
- representative corrected-form peaks were approximately `0.51`, `0.33`, and `0.12`;
- the corrected feasibility denominator approached roughly `0.15` in the preliminary run, which explains the sharp transient amplification.

### Current interpretation

The most conservative interpretation is an **equation/code or manuscript-specialization mismatch**: the general theory uses the correct derivative, while the printed Example 2 formula appears to omit the factor 2.

This does **not** establish fabrication or intentional manipulation.

---

## 5. Feasibility and numerical fragility

The predictor contains

```math
\frac{1}{1-\nabla D(P_1)f_1}.
```

Therefore, as

```math
\nabla D(P_1)f_1 \to 1,
```

both the predictor derivative and the control law can become very large. This is the mathematical reason for the regional feasibility condition and for the sharp control peaks visible in Example 2.

The paper explicitly proves only a regional result.

---

## 6. Region-of-attraction proof

The theorem constructs a region of attraction through several class-`K`, class-`KL`, and inverse-function bounds. The proof is bootstrap-like: estimates are first derived for trajectories satisfying the feasibility condition, and those estimates are then used to show that sufficiently small initial conditions remain inside the feasibility region.

This structure is standard in spirit, but for auditability a fully explicit maximal-feasibility-interval / first-exit argument would make the logical closure clearer.

Current status:

- no definite theorem-level contradiction has been established;
- the proof deserves a dedicated continuation/first-exit check before making a stronger claim.

---

## 7. Audit summary

| Item | Assessment |
|---|---|
| General predictor identity | Appears coherent under assumptions |
| Backstepping target dynamics | Appears coherent under assumptions |
| Plant generality | Strongly restricted strict-feedback class |
| Global stability | Not claimed; result is regional |
| Feasibility denominator | Potentially numerically fragile near delay-rate limit |
| Example 1 IC reporting | Potential discrepancy (`0.2` stated vs. ~`0.6` plotted) |
| Example 1 `T_eq` | Numerical value omitted from parameter sentence |
| Example 2 specialization | **Factor 2 appears missing in printed Eqs. (69)–(70)** |
| Fig. 4 reproduction | Preliminary evidence favors corrected factor-2 formula |
| Misconduct/fabrication | **No evidence established** |

---

## 8. Reproduction checklist

- [ ] Commit an executable reproduction of Example 1 with `X_2=0.2`.
- [ ] Commit the same run with `X_2=0.6` and compare against Fig. 3.
- [ ] Sweep plausible `T_eq` values and document which value matches the figure.
- [ ] Commit Example 2 using the **printed factor-1** equations.
- [ ] Commit Example 2 using the **corrected factor-2** equations.
- [ ] Save control-peak times/magnitudes for both cases.
- [ ] Run time-step refinement to distinguish equation mismatch from numerical artifacts.
- [ ] Archive all generated figures and environment/package versions.
- [ ] Perform a formal first-exit/continuation audit of the regional-stability proof.

---

## Citation

```bibtex
@article{bekiaris2012state,
  author  = {Bekiaris-Liberis, Nikolaos and Jankovic, Mrdjan and Krstic, Miroslav},
  title   = {Compensation of state-dependent state delay for nonlinear systems},
  journal = {Systems \& Control Letters},
  year    = {2012},
  volume  = {61},
  pages   = {849--856},
  doi     = {10.1016/j.sysconle.2012.05.002}
}
```
