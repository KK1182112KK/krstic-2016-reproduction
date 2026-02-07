"""Tests for predictor-based feedback implementation."""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from predictor import heun_predictor, run_pde_simulation, compute_Gamma


class TestHeunPredictor:
    """Test the Heun spatial integrator."""

    def test_analytical_U_zero(self):
        """With U=0 history, Z2 = exp(D)*X2 and Z1 = X1 + 2*(exp(D)-1)*X2."""
        D, N = 1.0, 1000
        X1, X2 = 1.0, 1.0
        u = np.zeros(N)

        Z1, Z2 = heun_predictor(X1, X2, u, D, N)

        Z2_exact = np.exp(D) * X2
        Z1_exact = X1 + 2 * (np.exp(D) - 1) * X2

        assert abs(Z2 - Z2_exact) < 1e-6, f"Z2 error: {abs(Z2 - Z2_exact)}"
        assert abs(Z1 - Z1_exact) < 1e-6, f"Z1 error: {abs(Z1 - Z1_exact)}"

    def test_convergence_order(self):
        """Heun method should converge at O(dx^2)."""
        D = 1.0
        X1, X2 = 1.0, 1.0
        Z2_exact = np.exp(D) * X2

        N_values = [50, 100, 200, 400]
        errors = []
        for N in N_values:
            u = np.zeros(N)
            _, Z2 = heun_predictor(X1, X2, u, D, N)
            errors.append(abs(Z2 - Z2_exact))

        # Check convergence rate: error should scale as (1/N)^2
        for i in range(len(errors) - 1):
            ratio = errors[i] / errors[i + 1]
            N_ratio = N_values[i + 1] / N_values[i]
            order = np.log(ratio) / np.log(N_ratio)
            assert order > 1.5, f"Convergence order {order:.2f} < 1.5 at N={N_values[i]}"

    def test_zero_state(self):
        """Zero state should give zero predictor."""
        D, N = 1.0, 100
        u = np.zeros(N)
        Z1, Z2 = heun_predictor(0.0, 0.0, u, D, N)
        assert abs(Z1) < 1e-15
        assert abs(Z2) < 1e-15


class TestSimulation:
    """Test the full simulation."""

    def test_convergence_to_origin(self):
        """Plant state should converge to origin."""
        t, X, U_hist, Z_hist = run_pde_simulation(D=1.0, N=100, t_end=20.0)
        assert np.linalg.norm(X[-1]) < 0.01, f"|X(t_end)| = {np.linalg.norm(X[-1])}"

    def test_gamma_decay(self):
        """Stability indicator should decay significantly."""
        t, X, U_hist, _ = run_pde_simulation(D=1.0, N=100, t_end=20.0)
        Gamma = compute_Gamma(t, X, U_hist, D=1.0)
        assert Gamma[-1] / Gamma[0] < 0.01, f"Gamma ratio: {Gamma[-1]/Gamma[0]}"

    def test_bounded_control(self):
        """Control input should remain bounded."""
        t, X, U_hist, _ = run_pde_simulation(D=1.0, N=100, t_end=20.0)
        assert np.max(np.abs(U_hist)) < 20, f"max|U| = {np.max(np.abs(U_hist))}"
