# Numerical files and columns

The main trajectory CSV header is:

`t,X1,X2,X3,U1,U2,P1X1,P1X2,P1X3,P2X1,P2X2,P2X3`

X is the original physical unicycle state, U1 turning rate, U2 speed; angles use radians and time uses seconds. P1/P2 are freshly reconstructed predictor endpoints in the compensated case. In uncompensated/delay-free cases the P slots are NaN by design: no delay predictors are calculated. These missing-diagnostic columns are not failed physical trajectories. Values at the last node are recorded controller evaluations, not an additional holding interval. Use REPORT.md for time conventions and error definitions.

Continuous-reference CSV columns: `t,X1,X2,X3`. They describe original delayed dynamics under continuous-time nominal uncompensated feedback, not an ideal stabilized target.

`summary.json`: all 17 main cases and numerical diagnostics. `continuous_reference.json`: three DOP853-tolerance cases. `refinement.json`: comparisons to the finest compensated trajectory. `uncompensated_refinement.json`: comparisons of seven sampled uncompensated runs to the finest continuous reference, reproduced by `postprocess.py` using linear interpolation of the saved reference grid. No interpolation-based difference is a rigorous exact-solution bound.

Figure-comparison CSV columns: `time,published_vector_curve,own_simulation`. `figure_audit/comparison.json` reports calibration-based differences, not discrepancies to author raw data. These are attributed derived comparison data, not the original PDF or authors' code. The optional extractor requires the exact supplied paper edition and explicit `--pdf` path.
