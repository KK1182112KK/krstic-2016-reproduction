# Equation-numbered audit index

This is an index of source-based findings and archived results, not an allegation of misconduct. Detailed reports live in the individual subprojects. A source equation, an algebraic consequence, a numerical experiment and a published figure are treated as different evidence categories.

## 1. 2016 Automatica paper

**[P16]** N. Bekiaris-Liberis and M. Krstic, *Stability of predictor-based feedback for nonlinear systems with distributed input delay*, 70 (2016), 195–203. DOI: `10.1016/j.automatica.2016.04.011`.

| Finding | Exact source location | Result / evidence | Classification and limit |
|---|---|---|---|
| Executed Example 1 | Physical **(28)–(29)**, feedback **(32)**, transform **(33)–(34)**; pp. 197–198 | At D=1, h=0.005, T=20, physical norm **0.0728144524**; [data](../results/direct-dde/summary.json) | Own sampled/ZOH run; not a reproduction of Fig. 1. |
| Transformation check | Transformed dynamics **(30)–(31)** with feedback **(32)**, p. 197 | Z-reference maximum componentwise errors: **0.0175168477, 0.00872341165, 0.00435302254** as h is halved | Finite refinement evidence, not a proof of Theorem 1. |
| Repository's delayed-command recording bug | Delayed term in **(29)** | **27 to 0** output mismatches; t/X/U/Z unchanged in the [archived regression](../results/verification-2026-09-07/boundary-regression.json) | A bug in our implementation, not in the paper. |
| Example 2 startup compatibility | **Solutions**, p. 196, with **(8)**; physical **(64)–(65)**, transform **(66)–(67)**, feedback **(70)–(71)**, Fig. 1 and parameter paragraph, p. 199 | Direct substitution gives **U(0+) = -13/3**, whereas the stated closed-interval initial history gives U0(0)=0 | Algebraic initialization/solution-class observation; no inference of manipulation. |
| General-theorem scope | Separation **(10)**, Assumption 2, feedback assumptions **(15)–(16)**, conclusion **(17)–(18)**; pp. 196–197 | Conditional stability transfer is stated in the paper | A restriction is not a circular-proof defect. No whole-theorem verification is claimed. |
| Distributed-delay scope | **(107)–(112)** and Type I extension **(113)–(116)**; p. 201; kernel representation footnote 5 | Formulas are supplied; the executed Example 1 here does not test them | Coverage limitation, not evidence that the equations fail. |

For the Fig. 1 conditions X1(0)=X2(0)=1 and zero input history, **(66)–(67)** give Z1(0)=2 and Z2(0)=1. Inserting these into **(70)** yields `U(0+)=-13/3`. Allowing a startup jump is a plausible solution convention, but that is not literally the continuous feedback-compatible history in the printed Solutions paragraph. The archived executable 2016 runner concerns Example 1, **(28)–(34)**.

## 2. 2012 Systems & Control Letters paper

**[P12]** N. Bekiaris-Liberis, M. Jankovic, and M. Krstic, *Compensation of state-dependent state delay for nonlinear systems*, 61 (2012), 849–856. DOI: `10.1016/j.sysconle.2012.05.002`.

| Finding | Exact source location | Result / evidence | Classification and limit |
|---|---|---|---|
| Cooling history discrepancy | **(63)–(66)**; parameter paragraph after **(65)** and **Fig. 3**, p. 854 | Text states history **0.2**; figure appears to start X2 near **0.6**. Archived U(0+) values are **1.535321435** and **0.996662866** respectively | Text/visual discrepancy plus own alternative-condition experiment. Exact author settings remain unknown. |
| Cooling setpoint reporting | T_eq appears in **(65)**; parameter paragraph on p. 854 omits its numerical value | **0.4** is an explicit audit hypothesis; both history runs finish near it at T=10 | Not a verified author parameter. |
| Factor-of-two specialization | Delay in **(67)** differentiated and substituted into general **(4)–(7)** versus printed **(69)–(70)** | Chain rule gives **2 r1 omega sin(omega s) cos(omega s)**; printed denominators omit the 2 | Algebraic discrepancy, not proof that the core theorem is false. |
| Numerical consequence of formula choice | Physical **(67)–(68)** unchanged; compare printed **(69)–(70)** with the derived alternative | At dt=0.00125, T=6, maxima **0.089605957** versus **0.503594135**; all refinement rows in [data](../results/state-delay-direct/summary.csv) | Own finite-horizon sampled maxima; no author code. |
| Feasibility | Denominator in **(4)–(7)**; condition **(12)** | Corrected-case minimum sampled endpoint denominator **0.155149816** at dt=0.00125 | Not a continuous infimum or proof that (12) holds everywhere. |
| Regional theorem | Assumptions 1–3; **(16)–(19)**, **(20)–(22)**, **(57)–(62)** | Nominal ISS, predictor feasibility, and an attraction-region condition are explicit | No numerical certification of (16), or completed first-exit proof audit, is supplied. |

The [detailed 2012 report](../state-delay-2012/README.md) gives the integrator, tolerances, guards, histories, run lengths and measured terminal states.

## 3. Artstein 1982 delayed-control reduction

**[A82]** Z. Artstein, *Linear Systems with Delayed Controls: A Reduction*, IEEE Transactions on Automatic Control, AC-27(4), 869–879 (1982), DOI `10.1109/TAC.1982.1103023`.

Full executable report: [Artstein 1982 audit](../artstein-1982-reproduction/REPORT.md).

| Finding | Exact source location | Result / evidence | Classification and limit |
|---|---|---|---|
| Mixed atomic/distributed reduction | **(5.7)–(5.9)** | Reconstruction error refines **4.02093e-9 → 2.51201e-10 → 1.56906e-11** | Strong numerical support for this tested specialization; not a proof of the abstract measure-theoretic theorem. |
| Harmonic-oscillator coefficient | **(2.1)–(2.3)** | Direct differentiation/general formula gives first coefficient `-sin(kappa h)/kappa`; the supplied scan prints `-sin(kappa h)`. At kappa=2, h=0.01 numerical errors are **1.21548e-9** derived vs **1.11005** printed. | Printed-specialization discrepancy; the two coincide at kappa=1. |
| Time-varying kernel argument | **(5.10)–(5.12)** | Transformation requires `B(t+sigma,sigma)` while the supplied scan prints `B(t+sigma,t)`. Audit errors at h=0.01: **3.06344e-12** vs **0.670611**. | Special-case formula discrepancy, not a failure of the general construction. |
| Nonmonotone input-time example | **(5.17), (5.21)–(5.22)** | Correct inverse branches are `(1±sqrt(1-4t))/2`; derived reduced reconstruction error **1.253e-12**, printed-example error **0.287275** at finest step. | Algebraic/specialization audit. |
| Final sampled oscillator claim | final paragraph on printed p. 879 / Example 8.2 | At `kappa h = 2pi`, continuous reduced rank is 2 but sampled rank is 0; exact held-flow simulation returns the nonzero initial state at integer samples. | Analytical counterexample to that final sampled-control exclusion condition, not to continuous-input controllability or the abstract reduction. |

The audit executes **27 cases**; [compact results](../artstein-1982-reproduction/results/summary.json) and [test evidence](../artstein-1982-reproduction/tests.log) are committed. Full CSV trajectories and figures are regenerated by the runner rather than duplicated in the parent repository.

## 4. Bekiaris-Liberis & Krstic 2017 multi-input nonlinear predictor

**[BK17]** N. Bekiaris-Liberis and M. Krstic, *Predictor-Feedback Stabilization of Multi-Input Nonlinear Systems*, IEEE Transactions on Automatic Control 62(2), 516–531 (2017), DOI `10.1109/TAC.2016.2558293`.

Full executable report: [2017 multi-input audit](../bekiaris-liberis-krstic-2017-reproduction/REPORT.md).

| Finding | Exact source location | Result / evidence | Classification and limit |
|---|---|---|---|
| Original unicycle plant | **(82)–(84)** | Physical delayed plant is directly advanced from the printed initial state/history; no target trajectory creates X. | Implementation basis. |
| First predictor identity | **(93)–(95), (99)–(101)** | `max ||P1(t)-X(t+D1)||_inf` is approximately **1e-14** or smaller in main held-input runs; off-grid delay case is about **6.1e-16**. | Numerical support for implemented constant-delay identity. |
| Second predictor identity | **(96)–(98)** | Residual refines **5.4176e-3, 2.71765e-3, 1.34828e-3, 6.7154e-4, 3.35125e-4** as sample period halves from 0.04 to 0.0025 s. | Consistent with sampled/ZOH approximation of the continuous predictor; not a formal convergence proof. |
| Clock negative control | time argument in **(98)** / feedback **(89)–(90)** | Deliberately using the wrong clock gives P2 residual about **0.01198** at h=0.005, versus **0.0006715** with source clock. | Audit-created negative control; not attributed to the paper. |
| Compensated published figures | **Figs. 3–4** | Finest run differs from vector-extracted curves by at most roughly **0.00252** for state components and **0.00527** for inputs. | Close figure reproduction, not author raw-data equality. |
| Initial compatibility | Theorems 1–2 versus Section VII zero histories | Printed closed-interval zero history gives endpoint 0, while feedback yields **U1(0+)≈-0.6649065**, **U2(0+)≈-0.6454945**. | Solution-class/startup convention issue, not proof of instability. |
| Uncompensated Fig. 5 | nominal laws **(85)–(88)** | Independent method-of-steps/DOP853 reference is close to the published curve early but has late component differences up to about **4.322, 5.440, 1.289** by 15 s. | Full-curve reproduction is not established; numerical sensitivity and unknown author solver prevent a causal attribution. |

This project is deliberately kept separate from Zhao 2022: **the implemented 2017 constant-delay central predictor identities refine in the expected direction.** [Seventeen main cases](../bekiaris-liberis-krstic-2017-reproduction/results/summary.json), three independent uncompensated references, figure-comparison metrics and [17-test evidence](../bekiaris-liberis-krstic-2017-reproduction/tests.log) are committed in compact form.

## 5. Zhao et al. 2022 state-dependent two-input predictor

**[Z22]** Y. Zhao, H. Gao, S. Xu and Y. Kao, *Predictor-feedback stabilization of two-input nonlinear systems with distinct and state-dependent input delays*, Automatica 144 (2022), 110479, DOI `10.1016/j.automatica.2022.110479`.

Full executable report: [Zhao 2022 audit](../zhao-2022-reproduction/REPORT.md).

| Finding | Exact source location | Result / evidence | Classification and limit |
|---|---|---|---|
| Claimed second-predictor identity | statement after **(12)** | Differentiating `P2(t)=X(t+D2(P2(t)))` requires denominator `1-grad D2(P2) g2`; printed **(12)** is a product containing an additional term. | Algebraic incompatibility under the paper's own asserted predictor/clock identities. |
| Literal-composition exact-trajectory diagnostic | **(7), (11), (12)** | At x0=0.2, exact implicit P2 = **0.10632902870502527**, literal printed P2 = **0.10633990646069874**, discrepancy **1.08778e-5**; clock-consistent alternative agrees to floating-point scale. | Cleaner numerical algebra diagnostic; not dependent on the traffic future-term closure. |
| Linear gain index | general **(11)**, linear **(25), (30)** | General design implies `B1 K1 P2`; **(30)** prints `B1 K2 P2`. | Printed linear-specialization mismatch. |
| Traffic implementation boundary | traffic equations and predictors | `printed_product` traffic variant must disclose a closure for the otherwise future-composed `g1(sigma2)` term; literal composition is tested separately. | No claim of an unambiguous execution of every printed traffic formula. |
| Nonlinear traffic hypotheses | nonlinear example versus theorem assumptions | The audit records forward-completeness and dimensional-normalization issues separately from the predictor algebra. | Applicability/scope issue; not a blanket theorem refutation. |

The GitHub publication contains executable source, the same locally re-executed tests, [18-case traffic summary](../zhao-2022-reproduction/evidence/summary.csv), [9-case literal-composition diagnostics](../zhao-2022-reproduction/evidence/algebra.csv), provenance and a Colab wrapper.

## 6. Evidence boundaries and provenance

A successful finite simulation does not prove asymptotic or exponential stability. A printed typo or a restricted theorem scope does not establish fabrication. Conversely, journal publication is not treated as a substitute for checking algebra, conditions and original-plant numerics.

The older 2012/2016 recorded solver snapshot is `6f812dc3c37a4255bb831f95260f519fa6fb402a`; [verification records](VERIFICATION_2026_09_07.md) identify the local and CI executions associated with that snapshot. The Artstein, 2017 and Zhao subprojects carry their own source hashes, execution logs or provenance files. Documentation changes do not silently extend a result to experiments that were not executed.

All subprojects follow [REPORTING_STANDARD.md](REPORTING_STANDARD.md): original authorship stays with the source paper, alternative formulas are explicitly labeled, no author-generated plots/PDFs are redistributed, and no misconduct claim is inferred from reproducibility findings.
