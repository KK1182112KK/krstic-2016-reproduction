# Predictor-Based Feedback for Nonlinear Systems with Input Delay
### Reproduction of Bekiaris-Liberis & Krstic (Automatica, 2016)

[![Open in MATLAB Online](https://www.mathworks.com/images/responsive/global/open-in-matlab-online.svg)](https://matlab.mathworks.com/open/github/v1?repo=KK1182112KK/krstic-2016-reproduction)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/KK1182112KK/krstic-2016-reproduction/blob/master/python/notebook.ipynb)
[![MATLAB Tests](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/workflows/matlab-ci.yml/badge.svg)](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/workflows/matlab-ci.yml)
[![Python Tests](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/workflows/python-ci.yml/badge.svg)](https://github.com/KK1182112KK/krstic-2016-reproduction/actions/workflows/python-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

This repository reproduces **Example 1** from:

> N. Bekiaris-Liberis and M. Krstic, "Stability of predictor-based feedback for nonlinear systems with distributed input delay," *Automatica*, vol. 70, pp. 195–203, 2016.

The paper addresses stabilization of nonlinear systems where the control input reaches the plant only after a delay *D*. A predictor-based feedback framework estimates the plant state *D* seconds into the future, enabling the controller to compensate for the delay. Two independent numerical methods are implemented and cross-validated to **6-digit agreement**.

## Reproducibility Audit

A separate technical note documents independent checks of the printed equations, theorem assumptions, simulation initialization, and related 2012 state-dependent state-delay examples:

**[`docs/REPRODUCIBILITY_AUDIT.md`](docs/REPRODUCIBILITY_AUDIT.md)**

The audit deliberately distinguishes reproducibility/reporting discrepancies from claims about mathematical validity or research misconduct.

## Key Results

### Compensated vs Uncompensated Control
The predictor-based controller (blue) successfully stabilizes the system, while the naive delay-free control law (red) diverges:

<!-- ![Baseline Comparison](matlab/results/baseline_comparison.png) -->

### Cross-Validation: Two Independent Methods Agree to 10⁻⁶
<!-- ![Cross-Validation](matlab/results/results_comparison.png) -->

### Robustness Across Delay Values
The controller stabilizes the system for D ∈ {0.5, 1.0, 1.5, 2.0}:
<!-- ![Delay Sweep](matlab/results/delay_sweep.png) -->

## Methods

Two independent implementations verify the predictor computation:

| Method | Predictor | Plant ODE | Time Step |
|--------|-----------|-----------|-----------|
| **Spatial ODE** | Heun method on Type II spatial ODE (Eq. 79–80) | `ode45` (adaptive RK4/5) | Adaptive |
| **Direct Integral** | Nested numerical quadrature of Eq. 33–34 | Fixed-step RK4 | Δt = 0.1 s |

**Control law**: U(t) = −2Z₂(t) − Z₁(t), where Z₁, Z₂ are predictor states.

## Quick Start

### MATLAB
```matlab
cd matlab
run_all          % Reproduce all results
run_all('test')  % Run validation tests only
run_all('fig')   % Generate figures only
```

### Python
```bash
pip install -r python/requirements.txt
jupyter notebook python/notebook.ipynb
```
Or click the **Open In Colab** badge above.

## Validation

| Metric | Value |
|--------|-------|
| Cross-method agreement (t > D) | **9.4 × 10⁻⁶** |
| Plant state convergence | \|X(t_end)\| < 10⁻⁶ |
| Γ(t) decay | > 99.9999% reduction |
| Heun convergence order | O(Δx²) confirmed |

## Project Structure

```
├── matlab/
│   ├── run_all.m              # One-click reproduction
│   ├── startup.m              # Auto path configuration
│   ├── src/                   # Core implementation
│   │   ├── heun_predictor.m   # Unified Heun spatial integrator
│   │   ├── closedloop_ode.m   # Full closed-loop ODE
│   │   ├── run_full_closedloop.m
│   │   ├── run_direct_closedloop.m
│   │   ├── run_uncompensated.m
│   │   ├── generate_figures.m # All figure generation
│   │   └── utils/
│   ├── tests/                 # Validation suite
│   └── results/               # Generated figures
├── python/
│   ├── notebook.ipynb         # Interactive Jupyter notebook
│   ├── src/                   # Python implementation
│   └── tests/                 # pytest suite
├── docs/
│   ├── REPRODUCIBILITY_AUDIT.md # Independent audit notes
│   ├── report.tex             # LaTeX report
│   ├── SPEC.md                # Paper specification
│   └── METHODS.md             # Numerical methods notes
├── shared/
│   └── test_data.mat          # Cross-language validation data
└── .github/workflows/         # CI for MATLAB + Python
```

## Report

See [`docs/report.pdf`](docs/report.pdf) for the full technical report including:
- Detailed mathematical derivation
- Compatibility condition analysis
- Convergence rate discussion
- Uncompensated baseline comparison

## Citation

```bibtex
@article{bekiaris2016stability,
  author  = {Bekiaris-Liberis, Nikolaos and Krsti\'{c}, Miroslav},
  title   = {Stability of predictor-based feedback for nonlinear systems with distributed input delay},
  journal = {Automatica},
  year    = {2016},
  volume  = {70},
  pages   = {195--203},
  doi     = {10.1016/j.automatica.2016.04.011}
}
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
