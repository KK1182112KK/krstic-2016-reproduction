# Verification record: delayed-input boundary fix

Project maintainer: **Kenshin Kotari**. Verification date: 2026-09-07.
Parent revision: `f3836c7ed1d03411fa92f302dfdc2b2f676061f5`.
This record concerns the independent numerical implementation, not authorship
of the published control theory or proof that any paper is false.

## Reproduced defect and correction

At a recorded command-arrival time, subtracting the delay can move the lookup
one floating-point value to the left. For example, `1.2 - 1.0` is represented
as `0.19999999999999996`. The old reporting lookup could therefore select the
command before the one issued at 0.2.

The corrected Python and MATLAB output paths compare physical time directly
with `issued_time + D`, using a right-continuous event convention. No epsilon,
rounding of D, or shift in the actual command time is introduced. The plant
RHS, controller, spatial predictor, and plant substep integration are unchanged.

For D=1, controller period=0.01, T=3, X0=[1,1], and zero prehistory:

| Check | Measured result |
|---|---:|
| Old delayed-output mismatches | 27 |
| Corrected delayed-output mismatches | 0 |
| Maximum old delayed-output error | 0.03967720350334325 |
| Physical X unchanged from parent | Bitwise identical |
| Applied U unchanged from parent | Bitwise identical |
| Reconstructed Z unchanged from parent | Bitwise identical |

These are results for the stated finite run, not universal claims about every
possible floating-point time grid. The baseline source was checked against its
Git blob hash `a31020198b02cbfdc7e970459dcb1d9a61b8f159` before execution.

## Executed checks

The twelve added Python regression cases produced **3 failures and 9 passes**
against the original implementation, then all passed after the fix. The complete
Python suite subsequently produced **45 passes**: the previous 33 tests plus
12 new regression cases. Six notebook code cells were executed successfully.

Cases include an exact arrival, a non-grid-aligned delay, zero delay, a delay
longer than the run, a delay shorter than the sample period, two prehistories,
a partial final step, and no premature command when an arrival lies just after
the current time. Existing input-delay and state-delay tests also ran.

[Raw Python test log](../results/verification-2026-09-07/python-tests.log),
[boundary metrics](../results/verification-2026-09-07/boundary-regression.json),
and [source/environment manifest](../results/verification-2026-09-07/manifest.json)
record this run. Older audit notes describe earlier verification stages; this
record supersedes their test-count and diagnostic-output status, not their
unrelated mathematical observations.

## Reproduce

From a full checkout containing the parent revision:

```bash
python -m pytest python/tests/ -q
python python/run_boundary_validation.py
# Optional direct comparison with the trusted parent implementation:
git show f3836c7ed1d03411fa92f302dfdc2b2f676061f5:python/src/direct_dde.py > /tmp/direct_dde_before.py
python python/run_boundary_validation.py --baseline-file /tmp/direct_dde_before.py
python python/run_direct_validation.py
```

The runners regenerate trajectory CSVs and JSON summaries. Do not overwrite
this dated verification snapshot when recording a new environment or run.
The notebook can also be executed in Colab; it runs the full Python test suite.

## Limits and attribution

MATLAB received the analogous source fix and regression tests but was not
executed locally. CI configuration and a successful CI run are separate facts;
check Actions logs before claiming a MATLAB pass. Local Python logs do not
certify other Python versions, physical robustness, a region of attraction,
or ideal continuous-time implementation. The 2016 controller remains sampled/ZOH.
The 2012 physical solver and its printed/corrected alternatives are unchanged.

The software citation identifies Kenshin Kotari as the implementation project's
author, with the two source papers listed separately as references. Development
and documentation were AI-assisted. No authors' original code or published
figures are distributed or claimed as original work here.
