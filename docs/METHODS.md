# Numerical Methods & Implementation Notes

## ODE Solver

### PDE Method
- **Solver**: MATLAB `ode45` (embedded Runge-Kutta 4(5), adaptive step)
- **Tolerances**: RelTol = 1e-6, AbsTol = 1e-8
- **MaxStep**: dx/2 (CFL condition for upwind PDE)

### Direct Method
- **Solver**: Fixed-step RK4 (custom implementation)
- **Time step**: dt = 0.01s (default), 0.1s for figure generation
- **Predictor**: MATLAB `integral()` with nested quadrature

## Spatial Discretization

### Actuator PDE (Transport Equation)
```
u_t = u_x,  x ∈ [0, D]
u(D,t) = U(t)  (boundary condition)
```
- **Scheme**: First-order upwind: du_i/dt = (u_{i+1} - u_i) / dx
- **Grid**: N = 100 uniform points, dx = D/N = 0.01
- **CFL**: dt_max = dx (for u_t = u_x with advection speed = 1)

### Predictor Spatial ODE
- **Method**: Heun (improved Euler, explicit trapezoidal)
- **Order**: O(dx²)
- **Grid**: Same N = 100 points as actuator PDE
- **Boundary handling**: At i=N, u_{N+1} extrapolated from u_N (O(dx) error at boundary)

## Numerical Pitfalls

### 1. Compatibility Condition Discontinuity
At t=0, U jumps from 0 to ~-9.9. This discontinuity propagates through
the actuator PDE as a sharp wavefront, reducing local convergence order
to O(dx) during t ∈ [0, D].

### 2. Nested Integral Vectorization
MATLAB's `integral()` passes vectors to the integrand. Inner integrals must
use for-loops over each element, as their bounds depend on the outer variable.

### 3. Control History Growing Unbounded
The direct method accumulates control history. Trimming to [t-2D, t] prevents
O(n²) memory growth without affecting predictor computation.

## Validation Strategy

### Three-Tier Testing
1. **Test A — Transport PDE**: Verify upwind scheme against analytical u(x,t) = U(t+x-D)
2. **Test B — Spatial Integration**: Fix analytical u, test only Heun predictor accuracy
3. **Test C — Cross-Method**: Compare PDE vs Direct methods end-to-end

### Convergence Studies
- **N-convergence**: Heun order verified as O(dx²) using N = 50...1000
- **Analytical comparison at t=0**: With U=0, exact Z2 = e^D · X2

## Performance Notes
- PDE method: ~2 seconds for 20s simulation (N=100)
- Direct method: ~30 seconds for 20s simulation (dt=0.1, nested quadrature)
- Figure generation: ~5 minutes for full suite (includes delay sweep)
