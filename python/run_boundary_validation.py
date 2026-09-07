"""Archive the delayed-output regression without fitting any paper figure.

Run from the repository root. Optional --baseline-file accepts a trusted copy
of python/src/direct_dde.py from the parent revision to check unchanged X/U/Z.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python/src'))
from direct_dde import simulate, held_value


def main(out: Path, baseline_file: Path | None = None) -> None:
    r = simulate(D=1., sample_dt=.01, t_end=3.)
    expected = np.full(len(r.t), r.history_value)
    for k, now in enumerate(r.t):
        for j in range(k + 1):
            if r.t[j] + r.D <= now:
                expected[k] = r.U[j]
    legacy = np.array([held_value(t-r.D, r.t[:k+1], r.U[:k+1], t,
                                  r.history_value) for k, t in enumerate(r.t)])
    np.testing.assert_array_equal(r.U_delayed, expected)
    report = {
        'parameters': {'D': 1., 'sample_dt': .01, 't_end': 3., 'X0': [1., 1.],
                       'negative_time_input': 0.},
        'legacy_lookup_mismatched_nodes': int(np.count_nonzero(legacy != expected)),
        'fixed_lookup_mismatched_nodes': int(np.count_nonzero(r.U_delayed != expected)),
        'max_legacy_output_error': float(np.max(np.abs(legacy-expected))),
        'python': platform.python_version(), 'numpy': np.__version__,
        'source_sha256': hashlib.sha256((ROOT/'python/src/direct_dde.py').read_bytes()).hexdigest(),
        'baseline_trajectory_comparison': 'not requested',
        'scope': 'Finite numerical regression of reported delayed input, not a stability proof.',
    }
    if baseline_file is not None:
        spec = importlib.util.spec_from_file_location('_verified_baseline', baseline_file)
        if spec is None or spec.loader is None:
            raise ValueError('Cannot load baseline Python module.')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        b = module.simulate(D=1., sample_dt=.01, t_end=3.)
        equality = {name: bool(np.array_equal(getattr(r, name), getattr(b, name)))
                    for name in ('t', 'X', 'U', 'Z')}
        if not all(equality.values()):
            raise AssertionError(f'Trajectories changed: {equality}')
        report['baseline_trajectory_comparison'] = equality
        report['baseline_source_sha256'] = hashlib.sha256(baseline_file.read_bytes()).hexdigest()
    out.mkdir(parents=True, exist_ok=True)
    (out/'boundary-regression.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    np.savetxt(out/'delayed-input-comparison.csv',
               np.column_stack((r.t, legacy, r.U_delayed, expected)), delimiter=',',
               header='t,legacy_lookup,fixed_lookup,arrival_time_oracle', comments='')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('results/boundary-validation'))
    parser.add_argument('--baseline-file', type=Path, default=None)
    args = parser.parse_args()
    main(args.out, args.baseline_file)
