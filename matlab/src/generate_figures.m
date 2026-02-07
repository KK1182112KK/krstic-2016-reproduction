function generate_figures(opts)
% GENERATE_FIGURES Unified figure generation for all scenarios
%
% Usage:
%   generate_figures()                    — Generate all figures (default)
%   generate_figures(struct('set','pde')) — PDE results only
%   generate_figures(struct('dpi',300))   — Higher resolution
%
% Options (struct fields):
%   set       - 'all' (default), 'pde', 'direct', 'comparison',
%               'baseline', 'sweep', 'phase', 'lyapunov'
%   dpi       - Resolution (default: 300)
%   outdir    - Output directory (default: '../results')
%   D         - Delay (default: 1)
%   N         - Grid points (default: 100)
%   t_end     - Simulation time (default: 20)
%   X0        - Initial state (default: [1;1])
%   dt_direct - Direct method time step (default: 0.1)

    if nargin < 1, opts = struct(); end

    % Defaults
    D         = getfield_default(opts, 'D', 1);
    N         = getfield_default(opts, 'N', 100);
    t_end     = getfield_default(opts, 't_end', 20);
    X0        = getfield_default(opts, 'X0', [1; 1]);
    dpi       = getfield_default(opts, 'dpi', 300);
    outdir    = getfield_default(opts, 'outdir', fullfile(fileparts(mfilename('fullpath')), '..', 'results'));
    fig_set   = getfield_default(opts, 'set', 'all');
    dt_direct = getfield_default(opts, 'dt_direct', 0.1);

    if ~exist(outdir, 'dir'), mkdir(outdir); end

    % Publication style
    set(groot, 'DefaultFigureColor', 'w');
    set(groot, 'DefaultAxesXColor', 'k');
    set(groot, 'DefaultAxesYColor', 'k');
    set(groot, 'DefaultTextColor', 'k');

    %% Run simulations as needed
    need_pde    = any(strcmp(fig_set, {'all','pde','comparison','baseline','sweep','phase','lyapunov'}));
    need_direct = any(strcmp(fig_set, {'all','direct','comparison'}));

    if need_pde
        fprintf('Running PDE simulation...\n');
        [t, X, U_history, Z_history] = run_full_closedloop(D, N, t_end, X0);
        Gamma = compute_Gamma(t, X, U_history, D);
    end

    if need_direct
        fprintf('Running direct integral simulation...\n');
        [t_d, X_d, U_d, Z_d] = run_direct_closedloop(D, dt_direct, t_end, X0);
        Gamma_d = compute_Gamma(t_d, X_d, U_d, D);
    end

    %% Generate requested figures
    if any(strcmp(fig_set, {'all', 'pde'}))
        fig_pde(t, X, U_history, Z_history, Gamma, D, N, t_end, dpi, outdir);
    end

    if any(strcmp(fig_set, {'all', 'direct'}))
        fig_direct(t_d, X_d, U_d, Z_d, Gamma_d, D, t_end, dpi, outdir);
    end

    if any(strcmp(fig_set, {'all', 'comparison'}))
        fig_comparison(t, Z_history, t_d, Z_d, t_end, dpi, outdir);
    end

    if any(strcmp(fig_set, {'all', 'baseline'}))
        fig_baseline(D, N, t_end, X0, t, X, Gamma, dpi, outdir);
    end

    if any(strcmp(fig_set, {'all', 'sweep'}))
        fig_delay_sweep(N, t_end, X0, dpi, outdir);
    end

    if any(strcmp(fig_set, {'all', 'phase'}))
        fig_phase_portrait(X, dpi, outdir);
    end

    if any(strcmp(fig_set, {'all', 'lyapunov'}))
        fig_lyapunov(t, X, Z_history, dpi, outdir);
    end

    % Cleanup defaults
    set(groot, 'Default', struct());
    fprintf('All requested figures saved to: %s\n', outdir);
end

%% ===== Individual Figure Functions =====

function fig_pde(t, X, U_history, Z_history, Gamma, D, N, t_end, dpi, outdir)
    fig = figure('Position', [100, 100, 1000, 600], 'Color', 'w');
    style_subplot(subplot(2,2,1), t, {X(:,1), X(:,2)}, {'b-','r--'}, ...
                  {'$X_1$','$X_2$'}, 't [s]', 'X', sprintf('Plant State (D=%.1f, N=%d)', D, N), t_end);
    style_subplot(subplot(2,2,2), t, {U_history}, {'k-'}, {}, 't [s]', 'U', 'Control Input', t_end);
    subplot(2,2,3);
    semilogy(t, Gamma, 'b-', 'LineWidth', 1.5);
    xlabel('t [s]', 'FontSize', 11); ylabel('$\Gamma(t)$', 'Interpreter', 'latex', 'FontSize', 11);
    title('Stability Indicator $\Gamma(t)$', 'Interpreter', 'latex', 'FontSize', 12);
    grid on; xlim([0 t_end]); set(gca, 'Color', 'w');
    style_subplot(subplot(2,2,4), t, {Z_history(:,1), Z_history(:,2)}, {'b-','r--'}, ...
                  {'$Z_1$','$Z_2$'}, 't [s]', 'Z', 'Predictor State', t_end);
    export_fig(fig, fullfile(outdir, 'results_pde.png'), dpi);
end

function fig_direct(t_d, X_d, U_d, Z_d, Gamma_d, D, t_end, dpi, outdir)
    fig = figure('Position', [100, 100, 1000, 600], 'Color', 'w');
    style_subplot(subplot(2,2,1), t_d, {X_d(:,1), X_d(:,2)}, {'b-','r--'}, ...
                  {'$X_1$','$X_2$'}, 't [s]', 'X', 'Plant State (Direct)', t_end);
    style_subplot(subplot(2,2,2), t_d, {U_d}, {'k-'}, {}, 't [s]', 'U', 'Control Input', t_end);
    subplot(2,2,3);
    semilogy(t_d, Gamma_d, 'b-', 'LineWidth', 1.5);
    xlabel('t [s]', 'FontSize', 11); ylabel('$\Gamma(t)$', 'Interpreter', 'latex', 'FontSize', 11);
    title('Stability Indicator', 'Interpreter', 'latex', 'FontSize', 12);
    grid on; xlim([0 t_end]); set(gca, 'Color', 'w');
    style_subplot(subplot(2,2,4), t_d, {Z_d(:,1), Z_d(:,2)}, {'b-','r--'}, ...
                  {'$Z_1$','$Z_2$'}, 't [s]', 'Z', 'Predictor State', t_end);
    export_fig(fig, fullfile(outdir, 'results_direct.png'), dpi);
end

function fig_comparison(t, Z_history, t_d, Z_d, t_end, dpi, outdir)
    t_comp = 0:0.1:t_end;
    Z_pde_i = [interp1(t, Z_history(:,1), t_comp, 'pchip', 'extrap')', ...
               interp1(t, Z_history(:,2), t_comp, 'pchip', 'extrap')'];
    Z_dir_i = [interp1(t_d, Z_d(:,1), t_comp, 'pchip', 'extrap')', ...
               interp1(t_d, Z_d(:,2), t_comp, 'pchip', 'extrap')'];
    err_Z1 = abs(Z_pde_i(:,1) - Z_dir_i(:,1));
    err_Z2 = abs(Z_pde_i(:,2) - Z_dir_i(:,2));

    fig = figure('Position', [100, 100, 1000, 600], 'Color', 'w');

    subplot(2,2,1);
    plot(t_comp, Z_dir_i(:,1), 'b-', 'LineWidth', 1.5); hold on;
    plot(t_comp, Z_pde_i(:,1), 'r--', 'LineWidth', 1.2);
    xlabel('t [s]', 'FontSize', 11); ylabel('$Z_1$', 'Interpreter', 'latex', 'FontSize', 11);
    legend('Direct', 'PDE', 'Location', 'best', 'Interpreter', 'latex', 'FontSize', 10, 'TextColor', 'k');
    title('$Z_1$: PDE vs Direct', 'Interpreter', 'latex', 'FontSize', 12);
    grid on; set(gca, 'Color', 'w');

    subplot(2,2,2);
    plot(t_comp, Z_dir_i(:,2), 'b-', 'LineWidth', 1.5); hold on;
    plot(t_comp, Z_pde_i(:,2), 'r--', 'LineWidth', 1.2);
    xlabel('t [s]', 'FontSize', 11); ylabel('$Z_2$', 'Interpreter', 'latex', 'FontSize', 11);
    legend('Direct', 'PDE', 'Location', 'best', 'Interpreter', 'latex', 'FontSize', 10, 'TextColor', 'k');
    title('$Z_2$: PDE vs Direct', 'Interpreter', 'latex', 'FontSize', 12);
    grid on; set(gca, 'Color', 'w');

    subplot(2,2,3);
    semilogy(t_comp, max(err_Z1, 1e-15), 'b-', 'LineWidth', 1.2);
    xlabel('t [s]', 'FontSize', 11); ylabel('$|Z_1^{PDE} - Z_1^{Direct}|$', 'Interpreter', 'latex', 'FontSize', 11);
    title('$Z_1$ Absolute Error', 'Interpreter', 'latex', 'FontSize', 12);
    grid on; set(gca, 'Color', 'w');

    subplot(2,2,4);
    semilogy(t_comp, max(err_Z2, 1e-15), 'r-', 'LineWidth', 1.2);
    xlabel('t [s]', 'FontSize', 11); ylabel('$|Z_2^{PDE} - Z_2^{Direct}|$', 'Interpreter', 'latex', 'FontSize', 11);
    title('$Z_2$ Absolute Error', 'Interpreter', 'latex', 'FontSize', 12);
    grid on; set(gca, 'Color', 'w');

    export_fig(fig, fullfile(outdir, 'results_comparison.png'), dpi);
end

function fig_baseline(D, N, t_end, X0, t_comp, X_comp, Gamma_comp, dpi, outdir)
    % B3.1: Uncompensated baseline — delay-free control law applied naively
    fprintf('Running uncompensated baseline...\n');
    [t_uc, X_uc, U_uc] = run_uncompensated(D, N, t_end, X0);
    Gamma_uc = compute_Gamma(t_uc, X_uc, U_uc, D);

    fig = figure('Position', [100, 100, 1000, 500], 'Color', 'w');

    subplot(1,2,1);
    plot(t_comp, X_comp(:,1), 'b-', 'LineWidth', 1.5); hold on;
    plot(t_comp, X_comp(:,2), 'b--', 'LineWidth', 1.5);
    plot(t_uc, X_uc(:,1), 'r-', 'LineWidth', 1.5);
    plot(t_uc, X_uc(:,2), 'r--', 'LineWidth', 1.5);
    xlabel('t [s]', 'FontSize', 11); ylabel('State', 'FontSize', 11);
    legend('$X_1$ (compensated)', '$X_2$ (compensated)', ...
           '$X_1$ (uncompensated)', '$X_2$ (uncompensated)', ...
           'Interpreter', 'latex', 'FontSize', 9, 'Location', 'best', 'TextColor', 'k');
    title('Compensated vs Uncompensated Control', 'FontSize', 12);
    grid on; xlim([0, min(t_end, 10)]); set(gca, 'Color', 'w');

    subplot(1,2,2);
    semilogy(t_comp, Gamma_comp, 'b-', 'LineWidth', 1.5); hold on;
    semilogy(t_uc, Gamma_uc, 'r-', 'LineWidth', 1.5);
    xlabel('t [s]', 'FontSize', 11); ylabel('$\Gamma(t)$', 'Interpreter', 'latex', 'FontSize', 11);
    legend('Compensated', 'Uncompensated', 'Location', 'best', 'TextColor', 'k', 'FontSize', 10);
    title('Stability Indicator Comparison', 'FontSize', 12);
    grid on; xlim([0, min(t_end, 10)]); set(gca, 'Color', 'w');

    export_fig(fig, fullfile(outdir, 'baseline_comparison.png'), dpi);
end

function fig_delay_sweep(N, t_end, X0, dpi, outdir)
    % B3.2: Delay parameter sweep
    D_values = [0.5, 1.0, 1.5, 2.0];
    colors = {'b', 'r', [0 0.6 0], [0.8 0 0.8]};  % blue, red, green, purple
    styles = {'-', '--', '-.', ':'};

    fig = figure('Position', [100, 100, 1000, 500], 'Color', 'w');

    subplot(1,2,1); hold on;
    subplot(1,2,2); hold on;

    legends = cell(length(D_values), 1);
    for idx = 1:length(D_values)
        D_val = D_values(idx);
        fprintf('Sweep: D = %.1f...\n', D_val);
        [t_s, X_s, U_s, ~] = run_full_closedloop(D_val, N, t_end, X0);
        Gamma_s = compute_Gamma(t_s, X_s, U_s, D_val);

        subplot(1,2,1);
        plot(t_s, sqrt(X_s(:,1).^2 + X_s(:,2).^2), ...
             'Color', colors{idx}, 'LineStyle', styles{idx}, 'LineWidth', 1.5);

        subplot(1,2,2);
        semilogy(t_s, Gamma_s, ...
                 'Color', colors{idx}, 'LineStyle', styles{idx}, 'LineWidth', 1.5);

        legends{idx} = sprintf('$D = %.1f$', D_val);
    end

    subplot(1,2,1);
    xlabel('t [s]', 'FontSize', 11); ylabel('$|X(t)|$', 'Interpreter', 'latex', 'FontSize', 11);
    legend(legends, 'Interpreter', 'latex', 'Location', 'best', 'TextColor', 'k', 'FontSize', 10);
    title('State Norm vs Delay', 'FontSize', 12);
    grid on; xlim([0 t_end]); set(gca, 'Color', 'w');

    subplot(1,2,2);
    xlabel('t [s]', 'FontSize', 11); ylabel('$\Gamma(t)$', 'Interpreter', 'latex', 'FontSize', 11);
    legend(legends, 'Interpreter', 'latex', 'Location', 'best', 'TextColor', 'k', 'FontSize', 10);
    title('$\Gamma(t)$ vs Delay', 'Interpreter', 'latex', 'FontSize', 12);
    grid on; xlim([0 t_end]); set(gca, 'Color', 'w');

    export_fig(fig, fullfile(outdir, 'delay_sweep.png'), dpi);
end

function fig_phase_portrait(X, dpi, outdir)
    fig = figure('Position', [100, 100, 600, 500], 'Color', 'w');

    plot(X(:,1), X(:,2), 'b-', 'LineWidth', 1.5); hold on;
    plot(X(1,1), X(1,2), 'go', 'MarkerSize', 10, 'MarkerFaceColor', 'g');
    plot(X(end,1), X(end,2), 'rx', 'MarkerSize', 12, 'LineWidth', 2);
    plot(0, 0, 'k+', 'MarkerSize', 15, 'LineWidth', 2);
    xlabel('$X_1$', 'Interpreter', 'latex', 'FontSize', 12);
    ylabel('$X_2$', 'Interpreter', 'latex', 'FontSize', 12);
    legend('Trajectory', 'Initial', 'Final', 'Origin', ...
           'Location', 'best', 'TextColor', 'k', 'FontSize', 10);
    title('Phase Portrait', 'FontSize', 14);
    grid on; axis equal; set(gca, 'Color', 'w');

    export_fig(fig, fullfile(outdir, 'phase_portrait.png'), dpi);
end

function fig_lyapunov(t, X, Z_history, dpi, outdir)
    V_X = 0.5 * (X(:,1).^2 + X(:,2).^2);
    V_Z = 0.5 * (Z_history(:,1).^2 + Z_history(:,2).^2);

    fig = figure('Position', [100, 100, 700, 500], 'Color', 'w');

    semilogy(t, V_X, 'b-', 'LineWidth', 2); hold on;
    semilogy(t, V_Z, 'r--', 'LineWidth', 2);
    xlabel('t [s]', 'FontSize', 12);
    ylabel('$V(t)$', 'Interpreter', 'latex', 'FontSize', 12);
    legend('$V(X) = \frac{1}{2}(X_1^2 + X_2^2)$', ...
           '$V(Z) = \frac{1}{2}(Z_1^2 + Z_2^2)$', ...
           'Interpreter', 'latex', 'FontSize', 11, 'Location', 'best', 'TextColor', 'k');
    title('Lyapunov Function Decay', 'FontSize', 14);
    grid on; xlim([0, t(end)]); set(gca, 'Color', 'w');

    export_fig(fig, fullfile(outdir, 'lyapunov_decay.png'), dpi);
end

%% ===== Helpers =====

function style_subplot(ax, t, data, styles, labels, xlab, ylab, ttl, t_end)
    axes(ax);
    hold on;
    for i = 1:length(data)
        plot(t, data{i}, styles{i}, 'LineWidth', 1.5);
    end
    xlabel(xlab, 'FontSize', 11);
    ylabel(ylab, 'FontSize', 11);
    if ~isempty(labels)
        legend(labels, 'Interpreter', 'latex', 'Location', 'best', 'TextColor', 'k', 'FontSize', 10);
    end
    title(ttl, 'FontSize', 12);
    grid on; xlim([0 t_end]); set(gca, 'Color', 'w');
end

function export_fig(fig, filepath, dpi)
    exportgraphics(fig, filepath, 'Resolution', dpi, 'BackgroundColor', 'white');
    fprintf('Saved: %s\n', filepath);
    close(fig);
end

function val = getfield_default(s, field, default)
    if isfield(s, field)
        val = s.(field);
    else
        val = default;
    end
end
