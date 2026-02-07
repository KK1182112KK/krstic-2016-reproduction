%% RUN_ALL  One-click reproduction of all results
%
%  Usage:
%    run_all           — Run simulation + generate all figures
%    run_all('test')   — Run validation tests only
%    run_all('sim')    — Run simulation only (no figures)
%    run_all('fig')    — Generate figures only
%    run_all('all')    — Everything: simulation + figures + tests
%
%  Designed for both interactive use and CI pipelines.

function run_all(mode)
    if nargin < 1, mode = 'default'; end

    % Setup paths
    root = fileparts(mfilename('fullpath'));
    addpath(genpath(fullfile(root, 'src')));

    fprintf('=============================================\n');
    fprintf('  Bekiaris-Liberis & Krstic (2016) — Example 1\n');
    fprintf('  Predictor-Based Feedback for Nonlinear Systems\n');
    fprintf('=============================================\n\n');

    switch lower(mode)
        case 'default'
            run_simulation();
            run_figures();
        case 'sim'
            run_simulation();
        case 'fig'
            run_figures();
        case 'test'
            run_tests(root);
        case 'all'
            run_simulation();
            run_figures();
            run_tests(root);
        otherwise
            error('Unknown mode: %s. Use ''sim'', ''fig'', ''test'', or ''all''.', mode);
    end

    fprintf('\n=== Done ===\n');
end

function run_simulation()
    fprintf('\n--- Simulation ---\n');
    D = 1; N = 100; t_end = 20; X0 = [1; 1];

    % PDE method
    [t, X, U_hist, Z_hist] = run_full_closedloop(D, N, t_end, X0);
    Gamma = compute_Gamma(t, X, U_hist, D);

    fprintf('\nPDE Method Results:\n');
    fprintf('  |X(t_end)| = %.4e\n', norm(X(end,:)));
    fprintf('  max|U|     = %.4f\n', max(abs(U_hist)));
    fprintf('  Gamma decay: %.2f%%\n', (1 - Gamma(end)/Gamma(1))*100);

    % Direct method (coarser step for speed)
    [t_d, X_d, U_d, Z_d] = run_direct_closedloop(D, 0.1, t_end, X0);

    fprintf('\nDirect Method Results:\n');
    fprintf('  |X(t_end)| = %.4e\n', norm(X_d(end,:)));

    % Cross-validation
    t_comp = 0:0.1:t_end;
    Z_pde_i = interp1(t, Z_hist, t_comp, 'pchip');
    Z_dir_i = interp1(t_d, Z_d, t_comp, 'pchip');
    max_err = max(max(abs(Z_pde_i(t_comp > D, :) - Z_dir_i(t_comp > D, :))));

    fprintf('\nCross-Validation (t > D):\n');
    fprintf('  max|Z_PDE - Z_Direct| = %.4e\n', max_err);
end

function run_figures()
    fprintf('\n--- Generating Figures ---\n');
    generate_figures(struct('set', 'all', 'dpi', 300));
end

function run_tests(root)
    fprintf('\n--- Running Tests ---\n');
    test_dir = fullfile(root, 'tests');
    if exist(test_dir, 'dir')
        results = runtests(test_dir, 'IncludeSubfolders', true);
        disp(results);
        n_failed = sum([results.Failed]);
        if n_failed > 0
            error('%d test(s) failed.', n_failed);
        end
    else
        fprintf('No tests directory found at: %s\n', test_dir);
    end
end
