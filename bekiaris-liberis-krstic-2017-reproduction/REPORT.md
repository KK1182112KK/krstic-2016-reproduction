---
title: "Bekiaris-Liberis and Krstic 2017: Independent Simulation Audit"
author: "Original-plant reproduction project for Kenshin Kotari"
date: "9 September 2026"
---

## Executive assessment

**The implemented unicycle predictor construction is consistent with the original physical plant under sample-period refinement. This audit does not reproduce the nonvanishing predictor-identity discrepancy found in the separate Zhao state-dependent-delay project.** The constant-delay and state-dependent-delay papers must not be conflated.

Seventeen main numerical cases and three independent continuous-time uncompensated reference runs completed. **Seventeen tests passed.** Main compensated figures agree closely, but not exactly, with the published vector curves. The uncompensated response is much more numerically sensitive; its late-time figure is not exactly reproduced.

| Question | Finding |
|---|---|
| $P_1(t)=X(t+D_1)$ | Agrees to floating-point scale in the exact-held-flow simulations, including off-grid delays |
| $P_2(t)=X(t+D_2)$ | Error decreases approximately linearly as the feedback sampling period is halved |
| Nominal dynamics after $D_2$ | Post-run discrepancy decreases with sampling refinement |
| Published compensated state/input figures | Close quantitative agreement; no exact-author-code claim |
| Initial history compatibility | Printed zero history at time zero is not equal to the initial feedback command |
| Uncompensated Fig. 5 | Early response agrees closely; substantial late differences remain; discretization sensitivity is measured separately |
| Full general stability theorem | Not independently proved or refuted by these simulations |

All computations were executed locally using Python on a CPU. The supplied Colab notebook was not run on Google's service. No MATLAB or GitHub Actions execution, author-source-code access, or misconduct claim is made. Implementation and reporting were AI-assisted.

## 1. Source and scope

**[BK17]** N. Bekiaris-Liberis and M. Krstic, *Predictor-Feedback Stabilization of Multi-Input Nonlinear Systems*, IEEE Transactions on Automatic Control, 62(2), 516-531, February 2017. DOI: 10.1109/TAC.2016.2558293. The supplied sixteen-page published PDF is the source; equation numbering is not borrowed from an earlier preprint.

| Source | Executed implementation or check |
|---|---|
| (1)-(8), Section II | Constant-delay sequential predictor context |
| Theorems 1-2; Assumptions 1-3 | Scope and initial compatibility, not a complete proof audit |
| (82)-(84), p. 522 | Original physical unicycle in `physical_interval` |
| (85)-(88) | `nominal`: uncompensated and delay-free feedback |
| (89)-(92) | Sampled feedback from reconstructed $P_1,P_2$, with $t+D_i$ clocks |
| (93)-(95), (99)-(101) | `first_predictor`: exact piecewise-held physical flow |
| (96)-(98) | `second_predictor`: spatial RK4 with $\theta+D_2$ in $\kappa_1$ |
| Section VII and Figs. 3-5 | Main conditions and optional calibrated PDF-vector comparisons |

The general multi-input class, arbitrary delay orderings, all initial states, and the full Lyapunov proofs are outside this finite numerical audit. A separate linear-system implementation is not presented here.

## 2. Original physical model and specified conditions

The model is source (82)-(84):

$$\dot X_1=U_2(t-D_2)\cos X_3,\quad \dot X_2=U_2(t-D_2)\sin X_3,\quad \dot X_3=U_1(t-D_1).$$

Published main conditions are $D_1=0.5$, $D_2=1$, $X(0)=(0.5,0.5,0.5)^T$ and zero input histories. $U_1$ is turning rate and $U_2$ is speed. We retain the time-varying nominal control exactly:

$$M=X_1\cos X_3+X_2\sin X_3,\qquad Q=X_1\sin X_3-X_2\cos X_3,$$
$$\kappa_1(t,X)=-M^2\cos t-MQ(1+\cos^2t)-X_3,$$
$$\kappa_2(t,X)=-M+Q(\sin t-\cos t)+Q\kappa_1(t,X).$$

Predictor feedback is $U_1(t)=\kappa_1(t+D_1,P_1(t))$ and $U_2(t)=\kappa_2(t+D_2,P_2(t))$, as in (89)-(90). Gains are not adjusted to fit a figure. No actuator saturation or angle wrapping is added.

The compensated runner goes to **101 seconds**, providing one additional delay horizon beyond the published 100-second plot so both predictor identities can be assessed through time 100. Main sample periods are 0.04, 0.02, 0.01, 0.005 and 0.0025 seconds. Additional cases include off-grid delays, spatial-step refinement, an explicitly incorrect-clock diagnostic, the delay-free baseline and a 500-second run.

## 3. How each control sample is computed

At time $t_k$, integrate the first predictor from current physical $X(t_k)$ over physical prediction time $r\in[0,D_1]$, using only issued inputs $U_1(t_k+r-D_1)$ and $U_2(t_k+r-D_2)$. The history buffer has zero negative-time input and separate right-hand startup commands.

For constant held $w=U_1$ and $v=U_2$, the unicycle step is exact:

$$\Delta X_1=vh\,\operatorname{sinc}(wh/2)\cos(X_3+wh/2),$$
$$\Delta X_2=vh\,\operatorname{sinc}(wh/2)\sin(X_3+wh/2),\qquad\Delta X_3=wh.$$

The second predictor starts at the first endpoint and integrates over $r\in[D_1,D_2]$. It uses $U_2(t_k+r-D_2)$ from history and the known nominal law $\kappa_1(t_k+r,p)$. This is the source's $\theta+D_2$ time argument after reparameterization. A known future clock value is not future measured state or future issued input.

The second spatial IVP uses RK4 with maximum step equal to half the control period, split at history switches. A quarter-period spatial run is also executed. The physical plant is independently advanced by the exact held-input flow with intervals split wherever either delayed issued command changes. Off-grid delays are evaluated at their actual arrival times.

Only physical state is persistently propagated. Both predictors are reconstructed at each control sample. The independent nominal reference is computed **after** a physical run; it does not create the control or the state trajectory.

A request for an unissued input raises an error. Nonfinite commands or magnitude above $10^{12}$ are explicit numerical guards; none activated in the saved cases. This implementation is sampled/ZOH feedback, not an assertion of exact continuous-time feedback or fourth-order accuracy of the full closed loop.

## 4. Predictor identities and nominal dynamics

Define, over sample times with a future physical state available,

$$E_i=\max_k\|P_i(t_k)-X(t_k+D_i)\|_\infty.$$

Future physical state is evaluated only after the simulation, using the exact held-flow dense evaluation between saved nodes. In particular, the off-grid identity check is not contaminated by a linear-interpolation error at an arrival discontinuity.

A further diagnostic integrates the nominal delay-free nonlinear equations from the measured $X(D_2)$, on the original physical clock. Its maximum componentwise difference from the actual delayed run for $t\ge D_2$ is denoted $E_{\mathrm{nom}}$.

| Sample period | $E_1$ | $E_2$ | $E_{\mathrm{nom}}$ |
|---:|---:|---:|---:|
| 0.04 | 6.5763e-15 | 0.00541761 | 0.00626757 |
| 0.02 | 6.703e-15 | 0.00271765 | 0.00310958 |
| 0.01 | 1.4341e-14 | 0.00134828 | 0.00155097 |
| 0.005 | 2.7619e-14 | 0.00067154 | 0.00077452 |
| 0.0025 | 5.3589e-14 | 0.000335125 | 0.000387019 |

The first predictor has no unknown future feedback on its interval and agrees to floating-point scale in this held-input simulation. The second predicts a nominal continuous feedback action where the executed controller holds sampled commands. Its finite-period residual is therefore expected; the observed approximately factor-two improvement under halving is evidence of consistency, not a formal convergence theorem.

At period 0.01, halving the spatial RK4 step again changes the second-predictor error by only about $6.4\times10^{-12}$, while the dominant sampling residual is about $1.35\times10^{-3}$. The off-grid case $D_1=0.503$, $D_2=1.007$ gives $E_1\approx6.1\times10^{-16}$ and $E_2\approx1.34\times10^{-3}$.

An explicitly labeled negative control replaces the second predictor's $\theta+D_2$ clock by $\theta$. At period 0.005 its $E_2$ is about **0.01198**, versus **0.0006715** with the source clock. This is our deliberately changed implementation, not a mistake attributed to the paper.

## 5. Comparison to the published compensated figures

After inspecting the rendered PDF, line paths for Figs. 3-5 were extracted with PyMuPDF. Axis coordinates were fixed during the local audit; no OCR, parameter fitting, or hidden rescaling of a trajectory was used. Curves have finite typesetting precision and are not author raw data.

For the finest main run, the maximum discrepancies to Fig. 3 over the plotted interval are approximately 0.002516, 0.000964 and 0.000731 for $X_1,X_2,X_3$. For Fig. 4, they are approximately 0.002246 for $U_1$ and 0.005262 for $U_2$. These support close reproduction, not exact equality.

The compact public folder retains the numerical findings but does not redistribute digitized source curves or source-figure overlays. Those can be regenerated from the reader's own PDF using the separate full audit package.

The physical state norm at 100 seconds is not expected to be numerically zero: the paper claims asymptotic, not finite-time, stabilization. The separate 500-second sampled run ends at a norm about **0.08314**. This finite observation is consistent with slow decay, but neither proves nor disproves an infinite-horizon claim.

## 6. Startup compatibility is a separate issue

Theorems 1 and 2 require the initial histories to be compatible with the feedback at their endpoints. The simulation section nevertheless specifies zero histories on closed intervals ending at time zero.

For the stated physical state and zero prehistory, the first predictor is exactly $(0.5,0.5,0.5)^T$. Computing the second predictor and applying (89)-(90) gives

$$U_1(0^+)\approx-0.664906519,\qquad U_2(0^+)\approx-0.645494470.$$

These differ from $U_{10}(0)=U_{20}(0)=0$. The audit handles them as startup jumps: prehistory is zero for negative time, and the computed feedback is used at and after zero. The jumps arrive at the plant after the corresponding delays. They are never smeared into negative-time history.

This is a mismatch with the theorem's stated continuous/compatible solution class, **not** evidence that a useful piecewise-smooth physical solution is impossible. The simulations and identity refinement do not by themselves prove an extension of the theorem to this startup convention.

## 7. Uncompensated response: a sensitive numerical comparison

An independently implemented continuous-time reference directly solves the physical delayed model under $U_i(t)=\kappa_i(t,X(t))$. It uses the method of steps in 0.5-second segments, with DOP853 dense solutions retained for past-state queries. Each delayed command is calculated from past physical state and its historical clock. No predictor or stabilized target is used.

DOP853 relative tolerances $10^{-8},10^{-10},10^{-12}$, absolute tolerances 100 times smaller, and maximum physical step 0.01 give terminal norms agreeing at approximately $10^{-11}$ scale:

$$X(15)\approx(8.130073095,-13.894013820,-0.711293403)^T,\quad\|X(15)\|_2\approx16.113585785.$$

This is an independent numerical reference, not a rigorous exact-solution enclosure.

| Sample period | Terminal physical norm at 15 s | Maximum difference to continuous reference |
|---:|---:|---:|
| 0.01 | 13.56797 | 22.91105 |
| 0.005 | 3.341306 | 11.44367 |
| 0.0025 | 7.66686 | 12.26366 |
| 0.00125 | 9.552812 | 6.195963 |
| 0.000625 | 12.90681 | 3.261547 |
| 0.0003125 | 14.57332 | 1.846583 |
| 0.00015625 | 15.36383 | 0.9589919 |

The finest sampled trajectory approaches the independent continuous reference, but still has a substantial finite-period residual. A coarse-grid mismatch is not by itself evidence against the published equations.

The published Fig. 5 and the independent continuous reference differ by less than about 0.001 through five seconds and less than about 0.010 through ten seconds. By fifteen seconds the maximum differences reach about **4.322**, **5.440**, **1.289** for $X_1,X_2,X_3$ respectively. Thus a full-curve quantitative reproduction is **not** established, even though both exhibit a large uncompensated response.

The measured sensitivity to numerical realization makes a discretization explanation plausible, but the authors' numerical code, step and solver are not known from this audit. No specific cause or intent is inferred. A finite growing response alone also does not establish instability for every initial history.

## 8. Reproducibility package

| Numerical set | Cases | Range or purpose |
|---|---:|---|
| Main compensated predictor | 5 | Sample periods 0.04 through 0.0025 s |
| Sampled uncompensated controller | 7 | Sample periods 0.01 through 0.00015625 s |
| Additional main cases | 5 | Delay-free, off-grid delays, spatial refinement, wrong-clock diagnostic, long horizon |
| Independent continuous reference | 3 | DOP853 tolerances 1e-8, 1e-10, 1e-12 |

`audit.py` executes all 17 main cases and saves complete trajectories, including non-favorable comparisons. `continuous_reference.py` runs the three independent uncompensated DDE references. `postprocess.py` reproduces the uncompensated refinement table. The full audit archive also contains optional source-figure comparison tooling requiring the user's own paper PDF.

```bash
pip install -r requirements.txt
python audit.py --out results
python continuous_reference.py
python postprocess.py
python -m pytest -q test_audit.py
```

The public Colab notebook is a repository-based CPU re-execution wrapper. Execution on the Google Colab service is not claimed.

Tests cover exact held-flow integration against an independent IVP, zero-input pre-arrival physics, separate initial-predictor integration, explicit startup incompatibility, off-grid first-predictor identity, refinement, future-input rejection, horizon-prefix independence, an incorrect-clock negative control and invalid parameters.

**Conclusion:** the central implemented unicycle predictor equations and the compensated simulation are supported by this audit. The finite sample realization is not the exact continuous controller, initial endpoint compatibility needs a separate solution convention, and the late uncompensated figure is not quantitatively reproduced. These are distinct conclusions; none licenses classifying the entire paper as false or fully verified.
