# Artstein (1982): delayed-control reduction reproduction

Independent equation-to-simulation audit for Kenshin Kotari. Development and reporting were AI-assisted. Original theory remains attributed to Zvi Artstein.

**Read [REPORT.md](REPORT.md) before interpreting the results.** The audit directly integrates selected original delayed-control plants, reconstructs Artstein's reduction afterwards, and independently integrates the corresponding reduced equations. Printed special-case formulas are kept separate from the core reduction.

Source: Z. Artstein, *Linear Systems with Delayed Controls: A Reduction*, IEEE Transactions on Automatic Control, AC-27(4), 869–879 (1982), DOI 10.1109/TAC.1982.1103023.

## Re-run

```bash
pip install -r requirements.txt
python audit.py --out results
python -m pytest -q test_audit.py
```

[Colab notebook](colab.ipynb) | [Measured summary](results/summary.json) | [Provenance](results/provenance.json) | [Publication scope](PUBLICATION.md)

The GitHub publication is intentionally compact: executable source, tests, reports, logs, manifest and compact numerical evidence are committed; full regenerated CSV trajectories and binary figures from the supplied audit archive are not duplicated. `audit.py` regenerates them. The original paper PDF is not redistributed.

## Main measured conclusion

The tested core reductions agree under refinement, including mixed point/distributed input terms. Several printed special cases in the supplied scan do not agree with direct differentiation/general formulas, including the oscillator coefficient in (2.3), the time-varying kernel argument in (5.12), the nonmonotone example (5.21)–(5.22), and the final sampled-oscillator exclusion condition. These findings are not presented as a refutation of the abstract reduction theorem.
