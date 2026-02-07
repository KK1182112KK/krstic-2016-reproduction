function [t_out, X_out, U_out, Z_out] = run_direct_closedloop(D, dt, t_end, X0)
% RUN_DIRECT_CLOSEDLOOP Run closed-loop with direct integral predictor
%
% Uses RK4 for plant dynamics and direct numerical quadrature (Eq. 33-34)
% for predictor computation.
%
% Inputs (optional):
%   D     - Delay time (default: 1)
%   dt    - Time step (default: 0.01)
%   t_end - End time (default: 20)
%   X0    - Initial state (default: [1; 1])
%
% Outputs:
%   t_out - Time vector (column)
%   X_out - State history [X1, X2]
%   U_out - Control history
%   Z_out - Predictor state history [Z1, Z2]

    if nargin < 1 || isempty(D), D = 1; end
    if nargin < 2 || isempty(dt), dt = 0.01; end
    if nargin < 3 || isempty(t_end), t_end = 20; end
    if nargin < 4 || isempty(X0), X0 = [1; 1]; end

    fprintf('Direct integral predictor simulation: D=%.2f, dt=%.4f, t_end=%.1f\n', D, dt, t_end);

    N_steps = ceil(t_end / dt);

    t_out = zeros(N_steps + 1, 1);
    X_out = zeros(N_steps + 1, 2);
    U_out = zeros(N_steps + 1, 1);
    Z_out = zeros(N_steps + 1, 2);

    t_out(1) = 0;
    X_out(1, :) = X0';
    U_out(1) = 0;

    % History: U(theta) = 0 for theta in [-D, 0)
    t_history = (-D : dt : -dt)';
    U_history = zeros(size(t_history));

    % Initial predictor at t=0
    t_hist_init = [t_history; 0];
    U_hist_init = [U_history; 0];
    [Z1_0, Z2_0] = predictor_direct(0, X0(1), X0(2), U_hist_init, t_hist_init, D);
    Z_out(1, :) = [Z1_0, Z2_0];
    U_out(1) = -2*Z2_0 - Z1_0;

    t_history = [t_history; 0];
    U_history = [U_history; U_out(1)];

    fprintf('Starting time integration...\n');
    tic;

    for k = 1:N_steps
        t_curr = (k-1) * dt;
        t_next = k * dt;

        X1 = X_out(k, 1);
        X2 = X_out(k, 2);
        U_curr = U_out(k);

        U_delayed = interp1(t_history, U_history, t_curr - D, 'linear', 'extrap');

        % RK4 for plant dynamics
        [X1_next, X2_next] = rk4_plant_step(X1, X2, U_curr, U_delayed, dt);

        t_out(k+1) = t_next;
        X_out(k+1, :) = [X1_next, X2_next];

        % Predictor at t_next
        [Z1_next, Z2_next] = predictor_direct(t_next, X1_next, X2_next, ...
                                              U_history, t_history, D);
        Z_out(k+1, :) = [Z1_next, Z2_next];
        U_next = -2*Z2_next - Z1_next;
        U_out(k+1) = U_next;

        t_history = [t_history; t_next];
        U_history = [U_history; U_next];

        % Trim old history
        keep_idx = t_history >= t_next - 2*D;
        t_history = t_history(keep_idx);
        U_history = U_history(keep_idx);

        if mod(k, round(N_steps/10)) == 0
            fprintf('  t = %.1f / %.1f (%.0f%%)\n', t_next, t_end, 100*k/N_steps);
        end
    end

    fprintf('Simulation complete. Elapsed: %.2f sec\n', toc);
end

function [X1_next, X2_next] = rk4_plant_step(X1, X2, U, U_delayed, dt)
    f1 = @(x1, x2) 2*x2 + U;
    f2 = @(x1, x2) (x2 + U_delayed) / (U_delayed^2 + 1);

    k1_1 = f1(X1, X2);
    k1_2 = f2(X1, X2);

    k2_1 = f1(X1 + 0.5*dt*k1_1, X2 + 0.5*dt*k1_2);
    k2_2 = f2(X1 + 0.5*dt*k1_1, X2 + 0.5*dt*k1_2);

    k3_1 = f1(X1 + 0.5*dt*k2_1, X2 + 0.5*dt*k2_2);
    k3_2 = f2(X1 + 0.5*dt*k2_1, X2 + 0.5*dt*k2_2);

    k4_1 = f1(X1 + dt*k3_1, X2 + dt*k3_2);
    k4_2 = f2(X1 + dt*k3_1, X2 + dt*k3_2);

    X1_next = X1 + (dt/6) * (k1_1 + 2*k2_1 + 2*k3_1 + k4_1);
    X2_next = X2 + (dt/6) * (k1_2 + 2*k2_2 + 2*k3_2 + k4_2);
end
