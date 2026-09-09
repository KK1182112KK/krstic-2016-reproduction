"""Reproduce the sampled/continuous uncompensated comparison from saved CSVs."""
from pathlib import Path
import argparse, json
import numpy as np

def main(folder: Path) -> None:
    ref = np.loadtxt(folder / 'uncompensated_continuous_tol1e-12.csv', delimiter=',', skiprows=1)
    rows = []
    for h in [.01, .005, .0025, .00125, .000625, .0003125, .00015625]:
        case = f'uncompensated_h{h}'
        a = np.loadtxt(folder / (case + '.csv'), delimiter=',', skiprows=1)
        if a[0, 0] < ref[0, 0] or a[-1, 0] > ref[-1, 0]:
            raise ValueError('Reference does not cover the sampled trajectory')
        r = np.column_stack([np.interp(a[:, 0], ref[:, 0], ref[:, j]) for j in [1, 2, 3]])
        rows.append(dict(case=case, final_norm=float(np.linalg.norm(a[-1, 1:4])),
                         max_component_error_to_continuous=float(np.max(np.abs(a[:, 1:4] - r)))))
    (folder / 'uncompensated_refinement.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(rows, indent=2))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', type=Path, default=Path('results'))
    main(ap.parse_args().results)
