function dydt = closedloop_ode(t, y, D, N)
% CLOSEDLOOP_ODE Full closed-loop ODE with PDE discretization
%
% State vector: y = [X1; X2; u_0; u_1; ...; u_{N-1}]
%
% Plant (Eq. 28-29):
%   dX1/dt = 2*X2 + U(t)
%   dX2/dt = (X2 + U(t-D)) / (U(t-D)^2 + 1)
%
% Actuator PDE (upwind): u_t = u_x, u(D,t) = U(t)
%
% Predictor (Eq. 79-80, Type II) solved via Heun method.
% Control law (Eq. 32): U = -2*Z2 - Z1

    X1 = y(1);
    X2 = y(2);
    u  = y(3:end);  % N elements

    dx = D / N;

    %% 1. Predictor via unified Heun method
    [Z1, Z2] = heun_predictor(X1, X2, u, D, N);

    %% 2. Control law
    U = -2*Z2 - Z1;

    %% 3. Plant dynamics
    u_delayed = u(1);  % u_0 = U(t-D)

    dX1 = 2*X2 + U;
    dX2 = (X2 + u_delayed) / (u_delayed^2 + 1);

    %% 4. Actuator PDE (upwind difference: u_t = u_x)
    du = zeros(N, 1);
    for i = 1:N-1
        du(i) = (u(i+1) - u(i)) / dx;
    end
    du(N) = (U - u(N)) / dx;  % Boundary: u(D,t) = U(t)

    dydt = [dX1; dX2; du];
end
