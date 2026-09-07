# Reproducibility Audit Notes

This document records independent checks of selected predictor-feedback papers by Bekiaris-Liberis, Jankovic, and Krstic that are relevant to this repository.

**Important:** these notes are about reproducibility, reporting consistency, structural assumptions, and numerical implementation. They are **not** allegations of misconduct. Where a discrepancy has a plausible benign explanation (for example, a typographical error or an omitted simulation parameter), that interpretation is stated explicitly.

---

## 1. Bekiaris-Liberis & Krstic, Automatica 70 (2016)

**Paper:** N. Bekiaris-Liberis and M. Krstic, “Stability of predictor-based feedback for nonlinear systems with distributed input delay,” *Automatica*, vol. 70, pp. 195–203, 2016.

**DOI:** `10.1016/j.automatica.2016.04.011`

### 1.1 Scope of the numerical example

The paper develops its main analysis first for

```math
\dot X(t)=f\bigl(X(t),U(t-D),U(t)\bigr),
```

and later explains how the approach extends to systems containing distributed-delay terms. The paper itself explicitly states that it focuses on systems without distributed-delay terms in the main development for clarity.

The published numerical simulation (Example 2 / Fig. 1) is therefore **not** a simulation of the genuinely distributed-delay extension. It uses the point-delay plant

```math
\dot X_1(t)=X_2(t)-X_2(t)^2U(t)-U(t-1),
\qquad
\dot X_2(t)=U(t).
```

Thus, the distributed-delay generalization is mathematically presented, but not directly demonstrated by a numerical example in the paper.

### 1.2 Compatibility condition versus simulation initialization

The paper’s solution framework assumes the initial input history is compatible with the feedback law:

```math
U_0(0)=\kappa\bigl(Z(0),U_0\bigr).
```

For Example 2, the paper states

```math
X_1(0)=X_2(0)=1,
\qquad
U(\theta)=0,\quad -1\le \theta\le 0.
```

The reduction is

```math
Z_1(t)=X_1(t)+X_2(t)-\int_{t-1}^{t}U(\theta)\,d\theta,
\qquad
Z_2(t)=X_2(t),
```

with feedback

```math
U(t)=-Z_1(t)-2Z_2(t)-\frac13Z_2(t)^3.
```

Therefore, with the stated initial history,

```math
Z_1(0)=2,
\qquad
Z_2(0)=1,
```

and hence

```math
U(0^+)=-2-2-\frac13=-\frac{13}{3}\approx -4.333.
```

But the stated history gives `U_0(0)=0`.

So, interpreted literally,

```math
U_0(0)=0 \neq \kappa(Z(0),U_0)\approx -4.333.
```

A natural interpretation is that the numerical simulation allows a startup jump in the control at `t=0`. This does **not** by itself invalidate the stability result, but it means that the simulation initialization is not literally identical to the compatibility condition used to obtain the stated regularity class in the theorem.

### 1.3 Direct numerical reproduction of Example 2

A direct method-of-steps implementation of the original delayed plant, using

```math
I(t)=\int_{t-1}^{t}U(\theta)\,d\theta,
\qquad
\dot I(t)=U(t)-U(t-1),
```

and the controller

```math
U(t)=-X_1(t)-3X_2(t)-\frac13X_2(t)^3+I(t),
```

reproduces the qualitative behavior of Fig. 1: the closed-loop states converge and the control starts near `-4.333` immediately after startup.

A preliminary independent run gave approximately

```text
max X1 ≈ 2.330 at t ≈ 1.69
min X2 ≈ -0.908 at t ≈ 1.30
X1(10) ≈ 0.0052
X2(10) ≈ -0.00147
```

which is consistent with the plotted response.

### 1.4 Structural restrictions worth keeping explicit

The main theorem requires, among other conditions,

```math
f(X,\omega,\Omega)-f(X,\omega,0)=g(X,\Omega),
```

so the effect of the current input must separate from the delayed-input variable in a specific way. The paper explicitly notes that without this assumption the delayed input would remain explicitly in the transformed vector field and the reduction would lose its intended effect.

The global transformation also uses forward and backward completeness assumptions, and the stability theorem assumes that a feedback law stabilizing the transformed system is already available.

For the distributed-delay extension, the input-affine kernel is restricted to a finite separable form of the type

```math
B_{\mathrm{int}}(\theta,X)=\sum_{i=1}^{m}h_i(X)b_i(\theta).
```

These points do not make the theorem incorrect, but they materially limit its constructive generality.

---

## 2. Bekiaris-Liberis, Jankovic & Krstic, Systems & Control Letters 61 (2012)

**Paper:** N. Bekiaris-Liberis, M. Jankovic, and M. Krstic, “Compensation of state-dependent state delay for nonlinear systems,” *Systems & Control Letters*, vol. 61, pp. 849–856, 2012.

**DOI:** `10.1016/j.sysconle.2012.05.002`

### 2.1 Plant class is a strict-feedback architecture

The plant is restricted to

```math
\dot X_1(t)=f_1\bigl(t,X_1(t),X_2(t-D(X_1(t)))\bigr),
```

```math
\dot X_2(t)=f_2\bigl(t,X_1(t),X_2(t)\bigr)+U(t).
```

Thus the delayed state appears as the virtual input of the first subsystem, while the actual control enters through a scalar integrator-like second subsystem. This is substantially narrower than a general nonlinear state-delay system.

### 2.2 Feasibility condition and regional nature of the result

The predictor contains the denominator

```math
1-\nabla D(P_1)f_1,
```

and the analysis requires

```math
\nabla D(P_1)f_1<c<1.
```

This is fundamental: as the delay-rate term approaches one, the predictor map becomes singular. The paper therefore proves a **regional** result and estimates a region of attraction rather than establishing global stabilization for arbitrary initial conditions.

The theorem also assumes the existence of a nominal feedback `\kappa` that renders the delay-free virtual-input subsystem input-to-state stable.

### 2.3 Example 1: reported initial condition appears inconsistent with Fig. 3

The cooling example states

```math
X_1(0)=1,
\qquad
X_2(\theta)=0.2
```

on the initial delay interval.

However, Fig. 3 visibly starts `T_in=X_2` close to `0.6`, not `0.2`. Since `X_2` is a state of an ODE, the plotted trajectory cannot continuously start from `0.2` and simultaneously appear near `0.6` at `t=0`.

A preliminary numerical reconstruction found that using

```math
X_2(\theta)=0.6
```

produces behavior much closer to the plotted response, including the initial control level and the open-loop equilibrium shown in Fig. 3.

The setpoint `T_eq` appears in the controller but its numerical value is not listed in the simulation-parameter sentence. The figure is consistent with approximately

```math
T_{eq}=0.4.
```

**Working interpretation:** likely a reporting/typographical error in the initial-history value plus an omitted simulation parameter. This should be confirmed with an archived reproduction script.

### 2.4 Example 2: algebraic factor-of-two discrepancy

Example 2 defines the state-dependent delay as

```math
D(s)=r_1\sin^2(\omega s).
```

Therefore

```math
D'(s)=2r_1\omega\sin(\omega s)\cos(\omega s).
```

The paper’s general predictor formula uses the denominator

```math
1-\nabla D(P_1)f_1.
```

Specializing that formula to Example 2 should therefore produce

```math
1-2r_1\omega\sin(\omega P_1)\cos(\omega P_1)v.
```

However, the printed specialized controller and predictor equations (69)–(70) use

```math
1-r_1\omega\sin(\omega P_1)\cos(\omega P_1)v,
```

with no factor `2`.

This is a direct algebraic inconsistency between the general formula and the printed specialization.

A preliminary numerical comparison found that the printed factor-1 specialization does not reproduce the prominent control spikes in Fig. 4, whereas the mathematically corrected factor-2 specialization produces spikes close to the plotted locations and magnitudes.

Preliminary corrected-form peak values were approximately

```text
0.51, 0.33, 0.12
```

for the first major positive spikes, and the corrected predictor denominator approached roughly `0.15` at its minimum during the run.

**Working interpretation:** the most conservative explanation is an equation/manuscript typo, potentially with the numerical code using the correct derivative. A stronger claim should not be made until the reproduction script and convergence checks are archived.

### 2.5 Core theory versus reporting quality

The central predictor identity

```math
P_1(t)=X_1\bigl(t+D(P_1(t))\bigr)
```

and the backstepping transformation leading to

```math
\dot Z_2=-c_2Z_2
```

appear structurally coherent under the stated feasibility and ISS assumptions.

The main concerns are therefore distinct:

1. the theory applies to a narrow strict-feedback plant class;
2. the feasibility condition creates an intrinsic singularity and only regional guarantees;
3. the region-of-attraction proof is written in a compact bootstrap style and would benefit from an explicit first-exit/continuation argument;
4. the numerical examples contain concrete reproducibility/reporting discrepancies.

---

## 3. Overall assessment

The evidence currently supports the following distinction:

| Question | Current assessment |
|---|---|
| Are the core transformations obviously wrong? | No. They appear mathematically coherent under the stated assumptions. |
| Are the assumptions restrictive? | Yes, materially so. |
| Is the theory highly constructive for general nonlinear delay plants? | No. The plant classes and nominal-stability assumptions are restrictive. |
| Are there reproducibility/reporting issues? | Yes. Several concrete discrepancies are documented above. |
| Is there evidence of fabrication or intentional manipulation? | No evidence established here. Typographical or manuscript/code mismatches remain plausible explanations. |

---

## 4. Reproduction tasks to archive next

- [ ] 2012 Example 1: script comparing initial histories `X2=0.2` and `X2=0.6`.
- [ ] 2012 Example 1: document the inferred/verified `T_eq` value.
- [ ] 2012 Example 2: factor-1 versus factor-2 numerical comparison.
- [ ] 2012 Example 2: timestep/solver convergence test for control peaks and minimum feasibility denominator.
- [ ] 2016 Example 2: archive the direct original-DDE method-of-steps reproduction.
- [ ] 2016 Example 2: explicitly compare compatible versus discontinuous startup histories.
- [ ] Add generated figures and a machine-readable summary table of all reproduction metrics.

---

## Reproducibility principle

The standard used in this audit is intentionally simple:

> A published predictor-feedback result should be testable by integrating the **original delayed plant**, evaluating only causal controller quantities available from the stated history and current state, and reproducing the reported behavior from the parameters and equations printed in the paper.

Agreement of a transformed or target system alone is not treated as a substitute for reproduction of the original delayed closed loop.
