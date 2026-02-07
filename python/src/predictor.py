"""Predictor-based feedback for nonlinear systems with input delay.

Reproduces Example 1 from Bekiaris-Liberis & Krstic (Automatica, 2016).

Two methods:
1. Spatial ODE (Heun method) — Type II predictor formulation
2. Direct integral quadrature — Explicit integration of Eq. 33-34
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d


def heun_predictor(X1: float, X2: float, u: np.ndarray, D: float, N: int):
    """Compute predictor states via Heun spatial integration.

    Solves:
        dp2/dx = (p2 + u(x)) / (u(x)^2 + 1),  p2(0) = X2
        dp1/dx = 2*p2,                           p1(0) = X1

    Args:
        X1, X2: Plant state (initial conditions for spatial ODE)
        u: Actuator state vector (N or N+1 elements)
        D: Delay time
        N: Number of spatial grid intervals

    Returns:
        Z1, Z2: Predictor states at x = D
    """
    dx = D / N

    # Extend u to N+1 if needed
    if len(u) == N:
        u_ext = np.append(u, u[-1])
    else:
        u_ext = u[:N + 1]

    p2, p1 = X2, X1

    for i in range(N):
        u_i = u_ext[i]
        u_ip1 = u_ext[i + 1]

        # Heun for p2
        f_p2_i = (p2 + u_i) / (u_i**2 + 1)
        p2_euler = p2 + dx * f_p2_i
        f_p2_ip1 = (p2_euler + u_ip1) / (u_ip1**2 + 1)
        p2_new = p2 + dx / 2 * (f_p2_i + f_p2_ip1)

        # Heun for p1
        k1 = 2 * p2
        k2 = 2 * p2_new
        p1_new = p1 + dx / 2 * (k1 + k2)

        p2, p1 = p2_new, p1_new

    return p1, p2  # Z1, Z2


def closedloop_ode(t, y, D, N):
    """Full closed-loop ODE with PDE discretization."""
    X1, X2 = y[0], y[1]
    u = y[2:]

    dx = D / N

    Z1, Z2 = heun_predictor(X1, X2, u, D, N)
    U = -2 * Z2 - Z1

    u_delayed = u[0]
    dX1 = 2 * X2 + U
    dX2 = (X2 + u_delayed) / (u_delayed**2 + 1)

    # Upwind PDE
    du = np.zeros(N)
    du[:-1] = (u[1:] - u[:-1]) / dx
    du[-1] = (U - u[-1]) / dx

    return np.concatenate([[dX1, dX2], du])


def run_pde_simulation(D=1.0, N=100, t_end=20.0, X0=None):
    """Run full closed-loop simulation using PDE method.

    Returns:
        t, X, U_history, Z_history
    """
    if X0 is None:
        X0 = np.array([1.0, 1.0])

    dx = D / N
    u0 = np.zeros(N)
    y0 = np.concatenate([X0, u0])

    sol = solve_ivp(
        lambda t, y: closedloop_ode(t, y, D, N),
        [0, t_end], y0,
        method='RK45',
        rtol=1e-6, atol=1e-8,
        max_step=dx / 2,
        dense_output=True
    )

    t = sol.t
    X = sol.y[:2].T
    u_all = sol.y[2:].T

    U_history = np.zeros(len(t))
    Z_history = np.zeros((len(t), 2))

    for k in range(len(t)):
        Z1, Z2 = heun_predictor(X[k, 0], X[k, 1], u_all[k], D, N)
        U_history[k] = -2 * Z2 - Z1
        Z_history[k] = [Z1, Z2]

    return t, X, U_history, Z_history


def compute_Gamma(t, X, U_history, D):
    """Compute Theorem 1 stability indicator."""
    n = len(t)
    Gamma = np.zeros(n)

    for k in range(n):
        X_norm = np.linalg.norm(X[k])
        mask = (t >= t[k] - D) & (t <= t[k])
        U_sup = np.max(np.abs(U_history[mask])) if np.any(mask) else np.abs(U_history[k])
        Gamma[k] = X_norm + U_sup

    return Gamma


def run_uncompensated(D=1.0, N=100, t_end=20.0, X0=None):
    """Run with naive delay-free control law (no predictor)."""
    if X0 is None:
        X0 = np.array([1.0, 1.0])

    dx = D / N
    u0 = np.zeros(N)
    y0 = np.concatenate([X0, u0])

    def ode(t, y):
        X1, X2 = y[0], y[1]
        u = y[2:]

        U = -2 * X2 - X1  # Naive control
        u_delayed = u[0]

        dX1 = 2 * X2 + U
        dX2 = (X2 + u_delayed) / (u_delayed**2 + 1)

        du = np.zeros(N)
        du[:-1] = (u[1:] - u[:-1]) / dx
        du[-1] = (U - u[-1]) / dx

        return np.concatenate([[dX1, dX2], du])

    sol = solve_ivp(ode, [0, t_end], y0, method='RK45',
                    rtol=1e-6, atol=1e-8, max_step=dx / 2)

    t = sol.t
    X = sol.y[:2].T
    U_history = -2 * X[:, 1] - X[:, 0]

    return t, X, U_history
