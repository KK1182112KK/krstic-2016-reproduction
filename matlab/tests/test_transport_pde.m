function [err_transport, results] = test_transport_pde(D, N, t_test, t_U0, U0, t_sim, U_sim)
% TEST_TRANSPORT_PDE Test A: Verify transport PDE discretization accuracy
%
% Checks that the actuator state u(x,t) from the upwind PDE discretization
% matches the analytical solution u(x,t) = U(t + x - D).
%
% Unlike the previous version which compared analytical to itself (trivially
% zero error), this version actually computes the PDE-discretized solution
% via forward Euler on the upwind scheme and compares against the analytical.
%
% Inputs:
%   D       - Delay time
%   N       - Number of spatial grid points
%   t_test  - Times to test (vector)
%   t_U0    - Initial history time grid (t < 0)
%   U0      - Initial history values
%   t_sim   - Simulation time grid (t >= 0)
%   U_sim   - Simulation control values
%
% Outputs:
%   err_transport - Maximum error over all test times
%   results       - Struct with detailed results

    dx = D / N;
    dt_pde = dx / 2;  % CFL condition: dt <= dx for u_t = u_x

    U_func = @(s) interp_control_history(s, t_U0, U0, t_sim, U_sim);

    n_tests = length(t_test);
    errors = zeros(n_tests, 1);
    results = struct();
    results.t_test = t_test;
    results.errors = zeros(n_tests, 1);
    results.u_analytic = cell(n_tests, 1);
    results.u_pde = cell(n_tests, 1);

    x_grid = (0:N-1)' * dx;

    for j = 1:n_tests
        t_k = t_test(j);

        % Analytical solution: u(x,t) = U(t + x - D)
        u_analytic = zeros(N, 1);
        for i = 1:N
            u_analytic(i) = U_func(t_k + x_grid(i) - D);
        end

        % PDE solution: simulate upwind scheme from t=0 to t=t_k
        % Initial condition at t=0: u(x,0) = U(x - D) for x in [0,D]
        u_pde = zeros(N, 1);
        for i = 1:N
            u_pde(i) = U_func(x_grid(i) - D);
        end

        % Time-step the PDE: u_t = u_x with upwind
        n_time_steps = ceil(t_k / dt_pde);
        dt_actual = t_k / max(n_time_steps, 1);

        for step = 1:n_time_steps
            t_step = step * dt_actual;
            % Boundary value: u(D, t) = U(t)
            U_boundary = U_func(t_step);

            du = zeros(N, 1);
            for i = 1:N-1
                du(i) = (u_pde(i+1) - u_pde(i)) / dx;
            end
            du(N) = (U_boundary - u_pde(N)) / dx;

            u_pde = u_pde + dt_actual * du;
        end

        % Compute error
        errors(j) = max(abs(u_pde - u_analytic));
        results.errors(j) = errors(j);
        results.u_analytic{j} = u_analytic;
        results.u_pde{j} = u_pde;
    end

    err_transport = max(errors);
    results.max_error = err_transport;

    fprintf('Test A (Transport PDE):\n');
    fprintf('  N = %d, dx = %.4f\n', N, dx);
    fprintf('  Test times: %s\n', mat2str(t_test, 2));
    fprintf('  Max error = %.2e\n', err_transport);
end
