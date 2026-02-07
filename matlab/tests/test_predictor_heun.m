function results = test_predictor_heun()
% TEST_PREDICTOR_HEUN Verify Heun predictor against direct integral at t=0
%
% At t=0 with U(theta) = 0 for theta in [-D,0], analytical solutions exist:
%   Z2 = exp(D) * X2
%   Z1 = X1 + 2*X2*(exp(D) - 1)

    fprintf('=== Test: Heun Predictor vs Analytical ===\n');

    D = 1;
    X1 = 1; X2 = 1;

    % Analytical (U=0 case)
    Z2_exact = exp(D) * X2;
    Z1_exact = X1 + 2*X2*(exp(D) - 1);

    N_values = [50, 100, 200, 500, 1000];
    errors = zeros(length(N_values), 2);

    for k = 1:length(N_values)
        N = N_values(k);
        u = zeros(N, 1);  % U(theta) = 0
        [Z1, Z2] = heun_predictor(X1, X2, u, D, N);
        errors(k, :) = [abs(Z1 - Z1_exact), abs(Z2 - Z2_exact)];
    end

    % Check convergence order
    ratios = errors(1:end-1, :) ./ errors(2:end, :);
    dx_ratios = N_values(2:end) ./ N_values(1:end-1);

    fprintf('\n  N      |Z1 err|       |Z2 err|\n');
    fprintf('  ----   ----------     ----------\n');
    for k = 1:length(N_values)
        fprintf('  %4d   %.4e     %.4e\n', N_values(k), errors(k,1), errors(k,2));
    end

    % Expect O(dx^2) = O(1/N^2) convergence
    expected_order = 2;
    actual_orders = log(ratios) ./ log(dx_ratios');
    mean_order = mean(actual_orders(:));

    fprintf('\n  Mean convergence order: %.2f (expected: %.1f)\n', mean_order, expected_order);

    results.N_values = N_values;
    results.errors = errors;
    results.mean_order = mean_order;
    results.passed = abs(mean_order - expected_order) < 0.5 && errors(end, 1) < 1e-6;

    if results.passed
        fprintf('  [PASS] Heun predictor converges at expected rate\n');
    else
        fprintf('  [FAIL] Convergence order or accuracy issue\n');
    end
end
