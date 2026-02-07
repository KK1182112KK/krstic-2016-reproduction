function [t, X, U_history, Z_history] = run_full_closedloop(D, N, t_end, X0)
% RUN_FULL_CLOSEDLOOP Run full closed-loop simulation (PDE method)
%
% Inputs (optional):
%   D     - Delay time (default: 1)
%   N     - Spatial grid points (default: 100)
%   t_end - Simulation end time (default: 20)
%   X0    - Initial state (default: [1; 1])
%
% Outputs:
%   t         - Time vector
%   X         - Plant state matrix (n x 2)
%   U_history - Control input history
%   Z_history - Predictor state history (n x 2)

    if nargin < 1 || isempty(D), D = 1; end
    if nargin < 2 || isempty(N), N = 100; end
    if nargin < 3 || isempty(t_end), t_end = 20; end
    if nargin < 4 || isempty(X0), X0 = [1; 1]; end

    dx = D / N;

    % Initial conditions: U(theta) = 0 for theta in [-D, 0]
    u0 = zeros(N, 1);
    y0 = [X0; u0];

    % ODE solver settings (CFL: MaxStep <= dx/2)
    options = odeset('RelTol', 1e-6, 'AbsTol', 1e-8, 'MaxStep', dx/2);

    fprintf('Running PDE simulation: D=%.2f, N=%d, t_end=%.1f...\n', D, N, t_end);
    [t, y] = ode45(@(t,y) closedloop_ode(t, y, D, N), [0, t_end], y0, options);
    fprintf('Simulation complete. %d time steps.\n', length(t));

    % Extract results
    X = y(:, 1:2);
    u_all = y(:, 3:end);

    % Recompute U(t) and Z(t) from stored actuator state
    U_history = zeros(length(t), 1);
    Z_history = zeros(length(t), 2);

    for k = 1:length(t)
        [Z1, Z2, U] = predictor_discrete(X(k,:)', u_all(k,:)', D, N);
        U_history(k) = U;
        Z_history(k, :) = [Z1, Z2];
    end
end
