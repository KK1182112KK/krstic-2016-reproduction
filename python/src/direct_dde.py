"""Original-plant simulation of Automatica 70 (2016), Example 1, Eqs. 28-34.

No transport PDE, independently propagated Z state, future X, or reduced-system
trajectory is used by this simulator. Only the two physical states are stepped.
The implemented controller is explicitly sampled and zero-order held (ZOH).
Its predictor is reconstructed from X and the actual held-input history at every
sample. This is NOT an exact simulation of the ideal continuous-time feedback.
Decrease sample_dt and inspect convergence before drawing conclusions.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class DirectResult:
    t: np.ndarray
    X: np.ndarray
    U: np.ndarray
    Z: np.ndarray
    U_delayed: np.ndarray
    D: float
    sample_dt: float
    history_value: float
    plant_method: str


def held_value(q: float, times: np.ndarray, values: np.ndarray,
               available_until: float, history_value: float = 0.0) -> float:
    """Right-continuous ZOH lookup; negative-time history never ramps to U(0+)."""
    if q > available_until + 1e-12 * max(1.0, abs(available_until)):
        raise ValueError('Future input-history access is forbidden.')
    if q < 0:
        return float(history_value)
    if len(times) == 0:
        if q == 0:
            return float(history_value)
        raise ValueError('No nonnegative-time input history is available.')
    i = np.searchsorted(times, q, side='right') - 1
    if i < 0:
        raise ValueError('Input history does not cover the requested time.')
    return float(values[i])


def predictor_from_history(t: float, X: np.ndarray, D: float,
                           times: np.ndarray, values: np.ndarray,
                           history_value: float = 0.0) -> np.ndarray:
    """Reconstruct (33)-(34) using exact affine spatial flow on each ZOH bin.

    Spatial IVP: p1'=2*p2, p2'=(p2+u)/(1+u**2), p(0)=X(t).
    The value of U at the single upper endpoint has zero integration weight.
    No extrapolation from a future control or a predicted physical X is used.
    """
    if D == 0:
        return np.asarray(X, dtype=float).copy()
    if D < 0 or t < 0 or len(times) != len(values):
        raise ValueError('Invalid predictor arguments.')
    if len(times) and times[-1] > t + 1e-12:
        raise ValueError('Predictor received future input samples.')
    lo = t - D
    first = np.searchsorted(times, lo, side='right')
    last = np.searchsorted(times, t, side='left')
    cuts = np.r_[lo, times[first:last], t]
    widths = np.diff(cuts)
    mids = 0.5 * (cuts[:-1] + cuts[1:])
    u = np.full(len(widths), float(history_value))
    mask = mids >= 0
    if np.any(mask):
        ii = np.searchsorted(times, mids[mask], side='right') - 1
        if np.any(ii < 0):
            raise ValueError('Missing input history on a predictor interval.')
        u[mask] = values[ii]
    a = 1.0 / (1.0 + u*u)
    ah = a * widths
    prefix = np.r_[0.0, np.cumsum(ah)]
    if prefix[-1] > 700:
        raise FloatingPointError('Predictor exponential exceeds floating-point range.')
    increment = u * np.expm1(ah) * np.exp(-prefix[1:])
    weighted_sum = np.r_[0.0, np.cumsum(increment)]
    p2_left = np.exp(prefix[:-1]) * (X[1] + weighted_sum[:-1])
    p2_end = np.exp(prefix[-1]) * (X[1] + weighted_sum[-1])
    gain = np.expm1(ah) / a
    p1_end = X[0] + 2.0 * np.sum((p2_left + u)*gain - u*widths)
    return np.array([p1_end, p2_end])


def plant_rhs(X: np.ndarray, U: float, U_delayed: float) -> np.ndarray:
    """The original physical plant, Eqs. (28)-(29), without substitution by Z."""
    return np.array([2.0*X[1] + U,
                     (X[1] + U_delayed)/(1.0 + U_delayed**2)])


def plant_step(X: np.ndarray, U: float, Ud: float, h: float,
               method: str = 'rk4') -> np.ndarray:
    if method == 'exact-held':
        # Independent check: exact integration of the ORIGINAL plant for
        # constant current/delayed controls on this subinterval, not a reduction.
        a = 1.0/(1.0 + Ud*Ud)
        e1 = np.expm1(a*h)
        return np.array([X[0] + 2*(X[1]+Ud)*e1/a - 2*Ud*h + U*h,
                         X[1] + (X[1]+Ud)*e1])
    if method != 'rk4':
        raise ValueError("plant_method must be 'rk4' or 'exact-held'.")
    k1 = plant_rhs(X, U, Ud)
    k2 = plant_rhs(X + h*k1/2, U, Ud)
    k3 = plant_rhs(X + h*k2/2, U, Ud)
    k4 = plant_rhs(X + h*k3, U, Ud)
    return X + h*(k1 + 2*k2 + 2*k3 + k4)/6


def simulate(D: float = 1.0, sample_dt: float = 0.01, t_end: float = 20.0,
             X0=(1.0, 1.0), history_value: float = 0.0,
             plant_method: str = 'rk4', compensated: bool = True) -> DirectResult:
    """Integrate physical X under causal, sampled predictor feedback.

    Constant negative-time input history is configurable. The delay is NEVER
    rounded to an integer number of samples. Each plant step is split at every
    delayed control-switch time inside it, including the startup jump at D.
    The final U is a sampled right-limit command; no step beyond t_end is taken.
    """
    X0 = np.asarray(X0, dtype=float)
    if X0.shape != (2,) or not np.isfinite(X0).all():
        raise ValueError('X0 must contain two finite physical states.')
    if not np.isfinite([D, sample_dt, t_end, history_value]).all():
        raise ValueError('All parameters must be finite.')
    if D < 0 or sample_dt <= 0 or t_end <= 0:
        raise ValueError('Require D >= 0, sample_dt > 0, t_end > 0.')
    if plant_method not in ('rk4', 'exact-held'):
        raise ValueError('Unknown plant_method.')
    n = int(np.ceil(t_end/sample_dt))
    t = np.minimum(np.arange(n+1)*sample_dt, t_end)
    X = np.empty((n+1, 2)); X[0] = X0
    Z = np.empty_like(X); U = np.empty(n+1); Ud = np.empty(n+1)
    for k in range(n+1):
        # Publish this control only AFTER reconstructing from strict past history.
        Z[k] = predictor_from_history(t[k], X[k], D, t[:k], U[:k], history_value)
        U[k] = -Z[k, 0]-2*Z[k, 1] if compensated else -X[k, 0]-2*X[k, 1]
        if not np.isfinite(np.r_[Z[k], U[k]]).all():
            raise FloatingPointError(f'Nonfinite controller at t={t[k]}; no clipping applied.')
        Ud[k] = held_value(t[k]-D, t[:k+1], U[:k+1], t[k], history_value)
        if k == n:
            break
        # Delayed commands can switch inside the step when D/dt is non-integer.
        shifts = t[:k+1] + D
        i = np.searchsorted(shifts, t[k], side='right')
        j = np.searchsorted(shifts, t[k+1], side='left')
        cuts = np.r_[t[k], shifts[i:j], t[k+1]]
        y = X[k].copy()
        for left, right in zip(cuts[:-1], cuts[1:]):
            delayed = held_value((left+right)/2-D, t[:k+1], U[:k+1],
                                 t[k+1], history_value)
            y = plant_step(y, U[k], delayed, right-left, plant_method)
        if not np.isfinite(y).all():
            raise FloatingPointError(f'Nonfinite plant at t={t[k+1]}; no clipping applied.')
        X[k+1] = y
    return DirectResult(t, X, U, Z, Ud, D, sample_dt, history_value, plant_method)


def identity_residual(result: DirectResult) -> np.ndarray:
    """Postprocessing only: per-time integral defect of the exact Z identity.

    Both endpoint RHS values use the held command on [t_k,t_{k+1}).
    The trapezoidal quadrature adds its own O(dt**2) normalized error.
    This is a numerical consistency diagnostic, NOT a proof or a controller.
    """
    z0, z1, u = result.Z[:-1], result.Z[1:], result.U[:-1]
    f0 = np.column_stack((2*z0[:, 1]+u, (z0[:, 1]+u)/(1+u*u)))
    f1 = np.column_stack((2*z1[:, 1]+u, (z1[:, 1]+u)/(1+u*u)))
    dt = np.diff(result.t)[:, None]
    return (z1-z0)/dt - (f0+f1)/2
