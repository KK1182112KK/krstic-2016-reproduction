---
title: "Artstein 1982: Equation-to-Simulation Audit"
author: "Independent reproduction project for Kenshin Kotari"
date: "9 September 2026"
---

## Executive assessment

**The core reduction agrees with independently integrated original plants in the tested examples. Several printed special-case formulas do not.** This distinction is essential: numerical agreement with selected instances is not a proof of the abstract theorem, and a faulty specialization is not, by itself, a refutation of the general construction.

The audit executed **27 numerical cases** and **16 tests passed**. Each case, including the discrepancies, is retained. The supplied article contains analytical examples, not numerical response figures; the present plots and numerical parameters are new audit experiments, not reproductions of author-generated simulations.

| Question | Finding |
|---|---|
| Mixed point/distributed input reduction, (5.7)-(5.9) | Agreement; maximum reconstruction error about $1.57\times10^{-11}$ in the finest tested run |
| Exponential unbounded memory, (2.4)-(2.6) | Agreement with the exact physical solution under refinement |
| Proportional delay $u(t/2)$, (5.13)-(5.15) | Agreement under refinement |
| Printed oscillator coefficient in (2.3) | Missing $\kappa^{-1}$ relative to direct differentiation of (2.2) |
| Printed time-varying kernel in (5.12) | Second argument $t$ disagrees with the $\sigma$ required by (5.10)-(5.11) |
| Nonmonotone example, (5.21)-(5.22) | Printed inverse roots and gain differ from general formula (5.17) |
| Final sampled-oscillator claim, p. 879 | Even multiples of $\pi$ must also be excluded; a full-cycle counterexample is retained |

All computations were executed in the local Python CPU environment. The Colab notebook is provided for re-execution but was not run on Google's service. No MATLAB or GitHub Actions execution, author-code access, misconduct finding, or complete proof audit is claimed. Development and reporting were AI-assisted.

## 1. Source, scope and equation-to-code map

**[A82]** Zvi Artstein, *Linear Systems with Delayed Controls: A Reduction*, IEEE Transactions on Automatic Control, AC-27(4), 869-879, August 1982. DOI: 10.1109/TAC.1982.1103023. This audit follows the supplied eleven-page scanned article. Formula details were checked on rendered pages, not inferred solely from its imperfect text extraction.

| Source | Code in `audit.py` | Role |
|---|---|---|
| (2.1)-(2.3), printed p. 870 | `oscillator` | Physical oscillator, integral reconstruction, printed and derived reduced equations |
| (2.4)-(2.6), p. 870 | `population` | Exact exponential-memory realization and reference solution |
| (5.1)-(5.3), p. 873; (6.1), p. 875 | `closed_loop` | Sampled feedback calculated from physical state and issued history |
| (5.7)-(5.9), p. 874 | `mixed` | Current atom, delayed atom and continuous density |
| (5.10)-(5.12), p. 874 | `time_varying` | Explicit time-dependent kernel and separate argument variants |
| (5.13)-(5.15), p. 874 | `proportional` | Proportional input-time map |
| (5.17), (5.21)-(5.22), pp. 874-875 | `folded` | Nonmonotone arrival map, two inverse branches |
| Example 8.2 and final conclusion, pp. 878-879 | `sampled_oscillator` | Exact held-forcing physical dynamics and rank diagnostic |

The abstract disintegration arguments in Theorems 3.3 and 8.1, all controllability/optimization claims, arbitrary matrix-valued kernels, and singular-continuous measures are **not** independently proved by these experiments. Parameters not supplied numerically by the source are explicitly audit choices below.

## 2. Numerical method and independence

Prescribed-input experiments use $u(t)=\sin(0.7t)+0.3\cos(1.9t)$, including negative time where required. Thus a past input can be evaluated without an interpolation ambiguity. Original physical states are advanced by RK4; the transformed state is reconstructed afterwards by Gauss-Legendre quadrature and compared with a separately integrated reduced equation. A reduced trajectory never generates the original physical state.

The general quadrature uses 48 nodes unless a case explicitly specifies 24. The mixed-measure experiment compares 24 and 48 nodes separately. The nonmonotone reduced integral is evaluated after a change of variable that removes its integrable endpoint singularity. No clipping of that singular gain is used.

The closed-loop scalar experiment instead maintains an issued-command buffer. At each sample it reconstructs the reduction from physical $x$ and past commands, computes the new command, and zero-order holds it. The original plant is integrated by its exact affine flow on intervals split at delayed command arrivals. Both an on-grid and an off-grid delay are tested. This is sampled feedback, **not** the ideal continuous-time law of Theorem 6.1. Sample-period errors and same-input identity errors are reported separately.

Unless stated otherwise, an error is the maximum absolute componentwise difference over stored times. These are floating-point diagnostics, not interval-certified bounds or continuous-time extrema.

## 3. Harmonic oscillator: a printed scaling discrepancy

The source's (2.1) is

$$\dot x=Ax+B u(t)+B u(t-h),\qquad A=\begin{bmatrix}0&1\\-\kappa^2&0\end{bmatrix},\quad B=\begin{bmatrix}0\\1\end{bmatrix}.$$

Differentiating the source transformation (2.2), or specializing general (5.3), gives

$$\dot y=Ay+(B+e^{-Ah}B)u(t),\qquad B+e^{-Ah}B=\begin{bmatrix}-\sin(\kappa h)/\kappa\\1+\cos(\kappa h)\end{bmatrix}.$$

Printed (2.3) instead has $-\sin(\kappa h)$ in the first component. The two agree when $\kappa=1$, which can conceal the discrepancy in a unit-frequency example. The audit therefore fixes $h=0.7$, $x(0)=(1,-0.2)^T$, $T=6$, and checks both $\kappa=1$ and $\kappa=2$ without changing any formula silently.

| RK4 step | Error using general-theory coefficient, $\kappa=2$ | Error using printed (2.3) |
|---:|---:|---:|
| 0.04 | 3.0384e-07 | 1.10981 |
| 0.02 | 1.91734e-08 | 1.11 |
| 0.01 | 1.21548e-09 | 1.11005 |

The persistent order-one difference is a specialization error, not a time-discretization error. The general-theory coefficient approaches the independently reconstructed trajectory.

**Own-figure note.** The executed audit package contains this generated plot; the public GitHub copy keeps the numerical source and compact metrics, and `audit.py` regenerates the figure.

## 4. Cases that agree with the reduction

### 4.1 Mixed Stieltjes input terms

The audit instance of (5.7)-(5.9) is scalar with $A=0.3$ and

$$dB(\theta)=0.4\delta_0(d\theta)-0.6\delta_{0.8}(d\theta)+(0.2+0.1\theta)\,d\theta,\quad 0\le\theta\le1.3.$$

The current atom is applied directly to the physical right-hand side, the delayed atom uses the same command at $t-0.8$, and the density is integrated independently. The initial physical state is 0.4, $T=5$. The reduced coefficient is computed as $\widehat B=\int e^{-A\theta}dB(\theta)$. The transformation is reconstructed by the corresponding finite-history integrals, not by assuming the reduced dynamics.

| Physical step | Maximum identity error |
|---:|---:|
| 0.04 | 4.02093e-09 |
| 0.02 | 2.51201e-10 |
| 0.01 | 1.56906e-11 |

At step 0.01, increasing quadrature from 24 to 48 nodes changes the error only at floating-point scale. This tests mixed atomic/absolutely-continuous terms, not a singular-continuous measure.

### 4.2 Unbounded exponential memory

For source (2.4), write $w(t)=\int_0^\infty e^{-\sigma}u(t-\sigma)d\sigma$. With zero input prehistory, $w(0)=0$ and $\dot w=u-w$ give an exact finite-dimensional realization of this particular physical convolution. We integrate

$$\dot x=x+w,\qquad \dot w=u-w,\qquad x(0)=1,\qquad u(t)=-4e^{-t}.$$

There is no memory-tail truncation. Direct analysis gives $w=-4te^{-t}$ and $x=(1+2t)e^{-t}$, while (2.5) becomes $y=x+w/2=e^{-t}$, in agreement with (2.6).

| Step, $T=10$ | Maximum physical-state error | Maximum reconstructed-$y$ error |
|---:|---:|---:|
| 0.04 | 0.000446309 | 0.000446309 |
| 0.02 | 2.80211e-05 | 2.80211e-05 |
| 0.01 | 1.75522e-06 | 1.75522e-06 |

The exponentially unstable homogeneous physical equation amplifies numerical cancellation error. Its reduction with refinement must not be misreported as a failure of the source identity.

### 4.3 Proportional delay

For (5.13)-(5.15), choose $A=0.3$, $B_0=0.4$, $B_1=0.8$, $x(0)=0.4$, $T=5$. Reconstruct

$$y(t)=x(t)+\int_{t/2}^t2e^{A(t-2s)}B_1u(s)ds.$$

The separately integrated equation is $\dot y=Ay+(B_0+2e^{-At}B_1)u(t)$. At steps 0.04, 0.02 and 0.01 the errors are approximately $1.44\times10^{-8}$, $9.01\times10^{-10}$ and $5.63\times10^{-11}$. This supports the tested formula, without asserting the correctness of every other specialization.

## 5. Time-varying kernel: argument mismatch in (5.12)

Source (5.10) uses a density $B(t,\sigma)$ and (5.11) reconstructs

$$y(t)=x(t)+\int_0^H\int_{t-\sigma}^{t}\Phi(t,s+\sigma)B(s+\sigma,\sigma)u(s)\,ds\,d\sigma.$$

Differentiation requires

$$\widehat B(t)=\int_0^H\Phi(t,t+\sigma)B(t+\sigma,\sigma)d\sigma.$$

The supplied scan prints $B(t+\sigma,t)$ in (5.12). This is different from the second argument in (5.11). The audit deliberately uses a kernel that depends on both arguments: $B(t,\sigma)=0.2+0.1t+0.3\sigma$, $A=0.2$, $H=0.7$, $x(0)=0.4$, $T=3$. This polynomial defines both variants wherever they are evaluated.

| Step | Error: $B(t+\sigma,\sigma)$ | Error: printed $B(t+\sigma,t)$ |
|---:|---:|---:|
| 0.04 | 7.84128e-10 | 0.670611 |
| 0.02 | 4.90052e-11 | 0.670611 |
| 0.01 | 3.06344e-12 | 0.670611 |

**Own-figure note.** The executed audit package contains this generated plot; the public GitHub copy keeps the numerical source and compact metrics, and `audit.py` regenerates the figure.

## 6. Nonmonotone input time: use both inverse branches

For source (5.21), $\theta(r)=r(1-r)$ on $[0,1]$. Solving $\theta(r)=t$ gives

$$r_\pm(t)=\frac{1\pm\sqrt{1-4t}}2,\qquad 0\le t<\frac14.$$

General (5.17) therefore gives, for the unit scalar drift,

$$\alpha(t)=\frac{e^{t-r_-(t)}+e^{t-r_+(t)}}{\sqrt{1-4t}}=\frac{2e^{t-1/2}\cosh(\sqrt{1-4t}/2)}{\sqrt{1-4t}}.$$

For $t>1/4$ there are no preimages and the coefficient is zero; the value at the single critical time can be assigned arbitrarily in the almost-everywhere ODE formulation. The singularity approaching that point is integrable.

Printed Example 5.7 omits the factor $1/2$ on the square-root terms in its inverse roots and prints a different coefficient, $2\sqrt{1-4t}\,e^{t-1/2}[e^{\sqrt{1-4t}}-e^{-\sqrt{1-4t}}]$. Neither agrees with direct substitution into (5.17).

The audit uses $a_0=0.4$, $a_1=0.8$, $x(0)=0.2$ and independently steps $\dot x=x+a_0u(t)+a_1u(t(1-t))$. The general transformation is reconstructed over future physical arrival times with already-issued input times. It is an offline identity test, not a controller using future measurements.

The reduced-reference integral is evaluated with $z=\sqrt{1-4t}$ to remove the integrable singularity. At step 0.0025 the general-theory reconstruction error is about $1.25\times10^{-12}$, whereas the printed-coefficient error remains about **0.287275**. Steps 0.01 and 0.005 yield the same persistent printed discrepancy.

**Own-figure note.** The executed audit package contains this generated plot; the public GitHub copy keeps the numerical source and compact metrics, and `audit.py` regenerates the figure.

## 7. Sampled oscillator: a counterexample to the final condition

The final paragraph on printed p. 879 claims that excluding only $\kappa h=(2j+1)\pi$ suffices even when commands remain constant for intervals of length $h$. Its displayed rank condition requires more: **$\sin(\kappa h)\ne0$**, excluding even multiples as well.

Take $h=1$, $\kappa=2\pi$ and $x(0)=(1,0)^T$. Over any one holding interval, both $u(t)$ and $u(t-1)$ are constant. The original physical oscillator completes a full period and

$$e^A=I,\qquad \int_0^1 e^{A(1-s)}B\,ds=0.$$

Thus $x(j+1)=x(j)$ for **every** command sequence, making settling an arbitrary nonzero initial state impossible. This is an analytical counterexample to that final special-case conclusion. It is not a counterexample to continuous-input controllability in Example 2.1.

| $\kappa h$ | Continuous reduced rank | Sampled reduced rank |
|---:|---:|---:|
| 1 | 2 | 2 |
| 1.5708 | 2 | 2 |
| 3.14159 | 0 | 0 |
| 6.28319 | 2 | 0 |
| 9.42478 | 0 | 0 |

An exact-flow simulation with $u_j=1+\sin j$ for eight holding intervals returns $x(8)=(1,1.47\times10^{-14})^T$. The finite floating-point value is consistent with the exact invariant, not the basis for proving it. The unsampled trajectory moves within each period; inspecting only smooth intra-period motion would miss the lost sampled controllability.

## 8. Closed-loop implementation and stability-transfer check

To illustrate (5.1)-(5.3) and (6.1), use the audit-chosen scalar plant

$$\dot x=x+u(t-h),\quad h=0.6,\quad x(0)=1,\quad u(s)=0\text{ for }s<0.$$

Here $\widehat B=e^{-h}$ and the ideal reduced feedback $u=Ky$, $K=-2e^h$, gives $\dot y=-y$. The executed controller is explicitly sampled and zero-order held. It reconstructs $y$ from physical $x$ and past commands and never reads an independent reference trajectory.

A separate exact reduced flow is driven by the **same issued commands**, and is compared with the reconstruction. A second reference $e^{-t}$ describes the ideal continuous-feedback solution and is used only to assess sampling effects.

| Sample period | Same-input identity discrepancy | Error to ideal $e^{-t}$ |
|---:|---:|---:|
| 0.04 | 7.69664e-11 | 0.0150156 |
| 0.02 | 5.16852e-11 | 0.00743191 |
| 0.01 | 2.01418e-09 | 0.00369728 |

The same-input identity stays close, although accumulated roundoff is amplified by the unstable homogeneous flow and need not decrease monotonically. The ideal-feedback discrepancy decreases approximately linearly with the sample period. An additional $h=0.613$ off-grid delay is split at actual arrivals rather than rounded to the control grid.

**Own-figure note.** The executed audit package contains this generated plot; the public GitHub copy keeps the numerical source and compact metrics, and `audit.py` regenerates the figure.

## 9. Reproducibility and evidence boundaries

Files in the full supplied audit package include `audit.py`, `test_audit.py`, `REPORT.md`, a PDF report, `colab.ipynb`, `results/summary.json`, case CSVs, figures and logs. The public GitHub copy is intentionally compact and keeps the executable source plus compact measured evidence; full trajectories and binary figures are regenerated by the runner.

```bash
pip install -r requirements.txt
python audit.py --out results
python -m pytest -q test_audit.py
```

The Colab notebook embeds the code and runs top to bottom on a CPU runtime, with optional Google Drive saving. No GPU is needed. Source PDFs and font files are excluded from the publication.

**Conclusion:** selected main reduction identities have strong numerical and elementary analytical support. The scanned article nevertheless has concrete printed-specialization errors, including a substantive final sampled-controllability overstatement. These should be corrected explicitly rather than silently implemented differently or used to dismiss the entire measure-theoretic theory.
