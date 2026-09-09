# Trajectory columns and interpretation

Artstein's paper provides analytical examples, not author numerical curves. Parameters are audit choices in REPORT.md. The trajectory CSVs deliberately preserve the executed arrays without a header. Column numbers below are **one-based**.

| File prefix | Columns in order |
|---|---|
| oscillator | t, physical x1, physical x2, reconstructed y1, reconstructed y2, derived reduced y1, derived reduced y2, printed reduced y1, printed reduced y2 |
| population | t, physical x, exponential-memory w, reconstructed y, exact y, exact x |
| mixed | t, physical x, reconstructed y, independently integrated reduced y |
| proportional | t, physical x, reconstructed y, independently integrated reduced y |
| time_varying | t, physical x, reconstructed y, derived reduced y, printed reduced y |
| folded | t, physical x, reconstructed y, derived reduced y, printed reduced y |
| closed_loop | t, physical x, issued u, reconstructed y, same-input reduced reference, ideal continuous-feedback reference |
| sampled_oscillator | t, physical x1, physical x2, constant forcing on the holding interval |

The final sampled-oscillator row retains the runner's terminal command convention; it is not a new post-horizon forcing evaluation. Read the analytical invariant in REPORT.md rather than using that column to infer an additional interval.

`summary.json` contains all 27 cases, parameters, completion status, wall time and case-specific errors. Each error is a maximum over stored times, not a continuous-time certificate. `derived` means our expression deduced from the source's general formula, not an author-issued corrigendum. `provenance.json` records the numerical environment and source hash. `MANIFEST.json` hashes this delivered snapshot.
