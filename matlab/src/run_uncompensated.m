function [t, X, U_history] = run_uncompensated(D, N, t_end, X0)
% RUN_UNCOMPENSATED Run closed-loop with delay-free control law (no predictor)
%
% Applies U(t) = -2*X2(t) - X1(t) directly, ignoring the input delay.
% This demonstrates that the naive (uncompensated) control law fails to
% stabilize the system when D > 0, motivating the predictor-based approach.
%
% The system is:
%   dX1/dt = 2*X2 + U(t)
%   dX2/dt = (X2 + U(t-D)) / (U(t-D)^2 + 1)
%
% with U(t) = -2*X2(t) - X1(t)  (no predictor compensation).
%
% Inputs:
%   D     - Delay time (default: 1)
%   N     - PDE grid points (default: 100)
%   t_end - Simulation time (default: 20)
%   X0    - Initial state (default: [1; 1])
%
% Outputs:
%   t         - Time vector
%   X         - State history (n x 2)
%   U_history - Control history (n x 1)

    if nargin < 1 || isempty(D), D = 1; end
    if nargin < 2 || isempty(N), N = 100; end
    if nargin < 3 || isempty(t_end), t_end = 20; end
    if nargin < 4 || isempty(X0), X0 = [1; 1]; end

    dx = D / N;

    % Initial conditions: U(theta) = 0 for theta in [-D, 0]
    u0 = zeros(N, 1);
    y0 = [X0; u0];

    options = odeset('RelTol', 1e-6, 'AbsTol', 1e-8, 'MaxStep', dx/2);

    fprintf('Running uncompensated baseline: D=%.2f, N=%d...\n', D, N);
    [t, y] = ode45(@(t,y) uncompensated_ode(t, y, D, N), [0, t_end], y0, options);

    X = y(:, 1:2);
    u_all = y(:, 3:end);

    % Recompute U(t) = -2*X2 - X1 (no predictor)
    U_history = -2*X(:,2) - X(:,1);
end

function dydt = uncompensated_ode(t, y, D, N)
    X1 = y(1);
    X2 = y(2);
    u  = y(3:end);
    dx = D / N;

    % Naive delay-free control law (no predictor)
    U = -2*X2 - X1;

    % Plant dynamics
    u_delayed = u(1);
    dX1 = 2*X2 + U;
    dX2 = (X2 + u_delayed) / (u_delayed^2 + 1);

    % Actuator PDE
    du = zeros(N, 1);
    for i = 1:N-1
        du(i) = (u(i+1) - u(i)) / dx;
    end
    du(N) = (U - u(N)) / dx;

    dydt = [dX1; dX2; du];
end
