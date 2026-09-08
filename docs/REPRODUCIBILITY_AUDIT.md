# Equation-numbered audit index

This is an index of source-based findings and archived results, not an allegation of misconduct. Detailed reports now live in [the 2016 project](../input-delay-2016/README.md) and [the 2012 project](../state-delay-2012/README.md). Those reports replace earlier preliminary numerical estimates with explicitly sourced, dated measurements. Historical wording remains available in Git history and is not a current numerical certificate.

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

### Example 2 analytical check, not an archived simulation result

For the Fig. 1 conditions X1(0)=X2(0)=1 and zero input history, **(66)–(67)** give Z1(0)=2 and Z2(0)=1. Inserting these into **(70)** yields

```math
U(0^+)=-2-2-\frac13=-\frac{13}{3}.
```

Allowing a startup jump is a plausible solution convention, but the initialization is not literally the continuous, feedback-compatible history in the **Solutions** paragraph. This calculation neither proves the theorem false nor establishes an unsuccessful simulation.

**Archive status:** the repository's direct solver and committed 2016 summary concern Example 1, **(28)–(34)**. An executable reproduction and numerical dataset for Example 2, **(64)–(71)**, have not been archived as part of that runner. Earlier conversational Example 2 peak values are not promoted here to verified project measurements.

## 2. 2012 Systems & Control Letters paper

**[P12]** N. Bekiaris-Liberis, M. Jankovic, and M. Krstic, *Compensation of state-dependent state delay for nonlinear systems*, 61 (2012), 849–856. DOI: `10.1016/j.sysconle.2012.05.002`.

| Finding | Exact source location | Result / evidence | Classification and limit |
|---|---|---|---|
| Cooling history discrepancy | **(63)–(66)**; parameter paragraph after **(65)** and **Fig. 3**, p. 854 | Text states history **0.2**; figure appears to start X2 near **0.6**. Archived U(0+) values are **1.535321435** and **0.996662866** respectively | Text/visual discrepancy plus own alternative-condition experiment. Exact author settings remain unknown. |
| Cooling setpoint reporting | T_eq appears in **(65)**; parameter paragraph on p. 854 omits its numerical value | **0.4** is an explicit audit hypothesis; both history runs finish near it at T=10 | Not a verified author parameter. |
| Factor-of-two specialization | Delay in **(67)** differentiated and substituted into general **(4)–(7)** versus printed **(69)–(70)** | Chain rule gives **2 r1 omega sin(omega s) cos(omega s)**; printed denominators omit the 2 | Algebraic discrepancy, not proof that the core theorem is false. |
| Numerical consequence of formula choice | Physical **(67)–(68)** unchanged; compare printed **(69)–(70)** with the derived alternative | At dt=0.00125, T=6, maxima **0.089605957** versus **0.503594135**; all refinement rows in [data](../results/state-delay-direct/summary.csv) | Own finite-horizon sampled maxima; no pixel fit and no access to author code. |
| Feasibility | Denominator in **(4)–(7)**; condition **(12)** | Corrected-case minimum sampled endpoint denominator **0.155149816** at dt=0.00125 | Not a continuous infimum or proof that (12) holds everywhere. Printed-factor denominator is not the true clock derivative. |
| Regional theorem | Assumptions 1–3; **(16)–(19)**, **(20)–(22)**, **(57)–(62)** | Nominal ISS, predictor feasibility, and an attraction-region condition are explicit | No numerical certification of (16), or completed first-exit proof audit, has been supplied here. |

The 2012 [detailed report](../state-delay-2012/README.md) states the actual integrator, tolerances, guard thresholds, histories, run lengths, and measured terminal states. The cooling open-loop curves and a full T=10 oscillatory figure comparison are not archived validations in the current results.

## 3. Evidence boundaries

A source equation, an algebraic consequence, a visual observation, and a numerical experiment are different evidence types. Each project follows [REPORTING_STANDARD.md](REPORTING_STANDARD.md). A successful finite simulation does not prove asymptotic stability, while a printed typo or restricted scope does not establish fabrication.

The source snapshot for the current recorded code/metrics is `6f812dc3c37a4255bb831f95260f519fa6fb402a`. [Verification records](VERIFICATION_2026_09_07.md) identify local execution; the CI runs linked from the root README identify later remote execution. Documentation changes do not silently extend either result to new experiments.
