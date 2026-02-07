# Specification: Bekiaris-Liberis & Krstic (2016)

## Reference
- **Authors**: Nikolaos Bekiaris-Liberis, Miroslav Krstic
- **Title**: Stability of predictor-based feedback for nonlinear systems with distributed input delay
- **Venue**: Automatica
- **Year**: 2016
- **DOI**: 10.1016/j.automatica.2016.04.010

## System Model (Example 1, Eq. 28-29)

Plant dynamics with input delay D:
```
dX1/dt = 2*X2 + U(t)
dX2/dt = (X2 + U(t-D)) / (U(t-D)^2 + 1)
```

## Predictor (Eq. 33-34)

Z2(t) = exp(∫[t-D,t] dθ/(U(θ)²+1)) · X2(t)
       + ∫[t-D,t] exp(∫[θ,t] ds/(U(s)²+1)) · U(θ)/(U(θ)²+1) dθ

Z1(t) = X1(t) + 2·∫[t-D,t] exp(∫[t-D,θ] ds/(U(s)²+1)) dθ · X2(t)
       + 2·∫[t-D,t] ∫[t-D,θ] exp(∫[s,θ] dr/(U(r)²+1)) · U(s)/(U(s)²+1) ds dθ

## Control Law (Eq. 32)
```
U(t) = -2*Z2(t) - Z1(t)
```

## Type II Predictor (Spatial ODE, Eq. 79-80)
```
dp2/dx = (p2 + u(x,t)) / (u(x,t)^2 + 1),  p2(0) = X2(t)
dp1/dx = 2*p2,                               p1(0) = X1(t)
Z_j(t) = p_j(D, t)
```

where u(x,t) = U(t + x - D) is the actuator state.

## Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| D | 1.0 s | Input delay |
| X(0) | [1, 1]ᵀ | Initial state |
| U(θ) | 0 for θ ∈ [-D, 0] | Input history |
| N | 100 | Spatial grid points |

## Stability Indicator (Theorem 1)
```
Γ(t) = |X(t)| + sup_{θ ∈ [t-D,t]} |U(θ)|
```
Must decay monotonically for stable closed-loop.

## Success Criteria
1. Both X1, X2 converge to 0
2. Γ(t) decays monotonically
3. Two independent methods agree to ≥ 5 significant digits for t > D
4. Heun spatial integrator shows O(Δx²) convergence
