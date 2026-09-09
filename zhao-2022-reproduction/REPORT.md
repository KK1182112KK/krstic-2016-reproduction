# Zhao et al. (2022): equation-to-simulation verification report

Prepared for Kenshin Kotari. Source calculations and original archive: 8 September 2026. Compact GitHub publication: 9 September 2026. AI-assisted implementation and reporting. Original theory, models and figures remain attributed to the original authors.

## 1. Source and evidence categories

[Z22] Y. Zhao, H. Gao, S. Xu and Y. Kao, *Predictor-feedback stabilization of two-input nonlinear systems with distinct and state-dependent input delays*, Automatica 144 (2022), 110479, DOI 10.1016/j.automatica.2022.110479. Equation numbers follow the supplied 12-page published PDF.

This report distinguishes: source statements; our algebraic derivations; archived numerical experiments; qualitative or quantitative comparisons to published plots; and unverified theorem-level claims. Neither an attractive plot nor a finite successful run proves asymptotic stability. No author simulation source code was obtained. This is not an allegation of misconduct.

| Source location | Implementation or assessment |
|---|---|
| (1), Assumptions 1-5, pp. 2-3 | Original problem class and theorem scope |
| (3)-(12), p. 3 | Sequential predictors; `prhs`, `integrate_predictor` |
| Identities following (12) | `inspect_run` and `exact_algebra_counterexample` |
| (13)-(15) | Numerical denominator diagnostics, not a certified continuous infimum |
| (24)-(31), p. 4 | Explicit printed/corrected gain variants |
| (42)-(43), p. 5 | Direct linear traffic DDE in `physical_rhs` |
| (44)-(47), pp. 6-7 | Direct nonlinear traffic DDE; units explicitly stated |
| Figs. 1,2,4,5,6,8 | Prior archive contains PDF-vector comparisons; these are not author raw data |
| Figs. 3,7 | Characteristic-field reconstruction, not an independently solved PDE |

## 2. Second-predictor identity and printed denominator

The source claims

$$P_2(t)=X(t+D_2(P_2(t))).$$

Writing g2 for the physical vector field at that predicted arrival, differentiation requires

$$\dot P_2=g_2(1+\nabla D_2(P_2)\dot P_2),\qquad \dot P_2=\frac{g_2}{1-\nabla D_2(P_2)g_2}.$$

Printed (12), however, uses

$$\Gamma_2=(1-\nabla D_1(P_2)g_1(\sigma_2))(1-\nabla(D_2-D_1)(P_2)g_2).$$

Under the predictor and clock identities asserted by the paper, substitution of the feedback gives g1(sigma2)=g2. Let a=grad(D1)g2 and b=grad(D2)g2. Then

$$\Gamma_{2,\mathrm{printed}}=(1-a)(1-b+a)=1-b+a(b-a).$$

The extra term a(b-a) is not generally zero. Thus the printed differential relation and the claimed identity cannot both hold for arbitrary admissible trajectories. This observation is about a specific formula/identity pair, not proof that every stabilization conclusion fails.

### Literal-composition diagnostic

An audit-chosen system isolates the algebra:

$$\dot X=-X+U_1+U_2,\quad \kappa_1=\kappa_2=0,$$
$$D_1(X)=0.3+0.15\tanh X,\quad D_2(X)=0.6+0.30\tanh X.$$

With zero inputs, X(t)=x0 exp(-t) is known. The delays are positive, smooth and ordered, the plant and partially closed plant are strongly forward-complete, and the nominal disturbed system is ISS. The true first predictor is obtained from its scalar implicit clock equation. The literal composed g1(sigma2) is evaluated from that known trajectory, **without** replacing it by g2 in the printed second-predictor calculation.

At x0=0.2, the exact second predictor is 0.10632902870502527. Printed (12) yields 0.10633990646069874; the clock-consistent alternative yields 0.10632902870502540. The printed error is 1.0877755673e-5 and persists at DOP853 tolerances 1e-8, 1e-10 and 1e-12 with maximum step 0.01. Initial states 0.1 and 0.05 yield smaller but nonzero errors. All nine rows are in [evidence/algebra.csv](evidence/algebra.csv).

No explicit numerical value of the theorem's attraction-region function psi(c) is certified. This diagnostic tests the asserted predictor identity; it does not purport to refute all regional stability conclusions.

## 3. Gain-index specialization and traffic interpretation

General (11) uses kappa1; (25) defines U1=K1 P1. The linear specialization must therefore contain B1 K1 P2. Printed (30) instead contains B1 K2 P2. The example has K1=90 and K2=60.

| Variant | Linear second-stage gain | Second-stage denominator |
|---|---|---|
| printed_product | Printed K2 | Printed product with disclosed closure |
| gain_only | K1 from general (11) | Same product |
| clock_consistent | K1 | 1-D2'(P2)g2 |

For nonlinear traffic, general (11) already uses K1; only the denominator differs.

**Important:** Traffic `printed_product` closes the otherwise future-evaluated g1(sigma2) as g2 using the very identity under audit. It is a disclosed consistency-closure interpretation, not an unambiguous reproduction of every printed expression. The preceding literal-composition diagnostic does not make this replacement and supplies separate algebraic evidence.

## 4. Original plants, parameters and numerical contract

The physical plant is directly stepped:

$$\dot X=\gamma X^2-b\{U_{in}(t-D_1(X))+U_{out}(t-D_2(X))\}.$$

Internal units are km and seconds. Road length=0.5 km, setpoint=0.2 km, b=0.00025 and speed=0.024 km/s. Linear delays: D1=l/speed, D2=(0.5-l)/speed. Nonlinear incoming delay: D1=(l+0.25 l^2)/speed, with the outgoing delay unchanged. Results are converted to meters for reporting.

Linear: gamma=0, K1=90, K2=60, X(0)=0.1, input prehistories=[8,12]. Nonlinear: K1=80, K2=50, X(0)=-0.15, prehistories=[0,0]. The main nonlinear convention is gamma=1 in km/second coordinates; gamma=1/3600 is a separate alternative because the printed X^2 term is not fully dimensionally normalized. Neither convention is asserted to be the authors' undisclosed code.

At every sample, reconstruct the first predictor from physical state and issued-input history, then reconstruct the second from the first endpoint. Predictor RK4 substeps are no larger than dt/2. Physical time uses four RK4 substeps per control sample. Commands are zero-order held and actual state-dependent delay values are queried. State-dependent arrival switches are **not** individually event-located within every physical substep. Therefore no fourth-order claim is made for the full closed loop. Rectangle-rule predictor variants are separately executed.

Future issued-input requests, nonpositive delays, negative predictor intervals and nonfinite or nonpositive/near-zero denominators raise errors. Denominator floor is 1e-8, a numerical guard rather than a feasibility proof. There is no clipping, hidden saturation or gain fitting. Denominator minima are over evaluated stages, not certified continuous extrema.

## 5. Archived results

After each physical run, evaluate

$$E_i=\max_{t_k+D_i(P_i(t_k))\le T}|P_i(t_k)-X(t_k+D_i(P_i(t_k)))|.$$

Future physical state is linearly interpolated **after** the run, never passed to the controller. See all 18 cases in [evidence/summary.csv](evidence/summary.csv).

| Nonlinear dt (s) | Printed-product E2 (m) | Clock-consistent E2 (m) |
|---:|---:|---:|
| 0.100 | 2.387891 | 0.030617 |
| 0.050 | 2.391469 | 0.016026 |
| 0.025 | 2.397786 | 0.008786 |

At dt=0.025, T=160 s, the respective final interfaces are 199.840060 m and 199.840225 m. Similar final road positions do not establish identical predictors.

| Linear variant, dt=0.025, T=200 s | Final interface (m) | E2 (m) |
|---|---:|---:|
| printed_product | 200.035892 | 0.379538 |
| gain_only | 200.038903 | 0.056984 |
| clock_consistent | 200.038897 | 0.011814 |

All 18 declared traffic runs completed, including two rectangle-rule cases and the hourly-drift alternative. The committed compact CSV preserves endpoints, both identity errors, denominator diagnostics and delay-order violation counts. Re-running audit.py saves richer JSON and full trajectories. It does not automatically certify bitwise equality to the archive.

## 6. Assumptions and source arithmetic

The linear example starts with D1=12.5 s and D2=8.3333 s, violating Assumption 1. The paper itself acknowledges this on pp. 5-6. A numerically causal startup does not retroactively satisfy a globally ordered-delay hypothesis. The known initial histories imply initial velocity -5 m/s and first incoming arrival 10.3448275862 s, consistent with the rounded 10.35 s.

For the nonlinear incoming delay at l(0)=50 m, the paper reports 2.63 s. The stated km/second convention gives 2.109375 s; literal meter substitution in the polynomial gives 28.125 s. This is a unit/reporting issue requiring clarification, not permission to fit a coefficient. The principal interpretation gives first arrival 4.84820014 s, close to the reported 4.85 s. Initial delay and first arrival horizon are different quantities.

With zero inputs and positive X(0), printed (47) has X(t)=X(0)/(1-X(0)t), so it is not globally strongly forward-complete as required in Assumption 3. With the stated linear feedback, the nominal quadratic system is not globally ISS either. A local reformulation might be possible; none is proved here.

## 7. Prior figure comparison and its limits

The prior private archive extracted PDF-vector line geometry for Figs. 1,2,4,5,6,8 after visually calibrating tick marks. No parameter fitting or OCR was used. Such coordinates are finite-precision published lines, not author raw data. They are not redistributed in this compact GitHub publication.

The nonlinear printed-product interpretation agreed closely with the displayed Fig. 6 input curves: maximum differences about 0.01360 and 0.00599 vehicles/km. Fig. 8's displayed second predictor was about 0.101 m from that interpretation versus 2.275 m from the clock-consistent alternative. Matching a published predictor curve is not the criterion for the physical predictor identity. The exact trajectory diagnostic above is independent of the plotted curves.

These comparison numbers describe the previous archive, not a newly executed figure comparison in this publication step. Full figure-comparison scripts and graphics remain in the separately supplied 8 September archive; this public runner regenerates its own physical trajectories and plots.

## 8. Reproducibility and interpretation

The unchanged test suite passed 14 tests in the original archive and again during the 9 September publication check. See [evidence/recheck-tests.log](evidence/recheck-tests.log). These tests cover exact pre-arrival trajectories, initial arithmetic, explicit gain variants, literal-composition diagnostics, causal rejection and prefix independence. Tests are not formal proofs.

Use `pip install -r requirements.txt`, `python -m pytest -q test_audit.py`, and `python audit.py --out regenerated-results`. The CPU Colab notebook runs these commands from the public repository. Colab itself and GitHub Actions were not run during this publication step. No MATLAB execution or author-code access is claimed.

The specific printed formula/identity incompatibility is the strongest finding. A corrected general theorem and its complete attraction-region proof remain separate tasks. Do not extrapolate the finite traffic tables into a proof that every theorem is false, or into any allegation of misconduct. Publication provenance and deliberately omitted binary artifacts are stated in [PUBLICATION.md](PUBLICATION.md).
