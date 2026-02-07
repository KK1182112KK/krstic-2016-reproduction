function [Z1, Z2] = predictor_direct(t, X1, X2, U_history, t_history, D)
% PREDICTOR_DIRECT Compute predictor via direct integral formulas (Eq. 33-34)
%
% Uses MATLAB's integral() with nested quadrature.
%
% Inputs:
%   t         - Current time
%   X1, X2    - Current plant states
%   U_history - Control input history (vector)
%   t_history - Time points for history (vector)
%   D         - Delay time
%
% Outputs:
%   Z1, Z2    - Predictor states

    t_start = t - D;
    U_func = @(s) interp1(t_history, U_history, s, 'linear', 'extrap');

    f = @(u) 1 ./ (u.^2 + 1);
    g = @(u) u ./ (u.^2 + 1);

    %% Z2 (Eq. 34)
    integral_1 = integral(@(theta) f(U_func(theta)), t_start, t, ...
                          'RelTol', 1e-6, 'AbsTol', 1e-9);
    term1_Z2 = exp(integral_1) * X2;

    integrand_Z2 = @(theta) exp_integral_to_t(theta, t, U_func, f) .* g(U_func(theta));
    term2_Z2 = integral(integrand_Z2, t_start, t, ...
                        'RelTol', 1e-6, 'AbsTol', 1e-9, 'ArrayValued', true);

    Z2 = term1_Z2 + term2_Z2;

    %% Z1 (Eq. 33)
    integrand_term2 = @(theta) exp_integral_from_tD(theta, t_start, U_func, f);
    integral_term2 = integral(integrand_term2, t_start, t, ...
                              'RelTol', 1e-6, 'AbsTol', 1e-9, 'ArrayValued', true);
    term2_Z1 = 2 * integral_term2 * X2;

    integrand_term3 = @(theta) inner_integral_Z1(theta, t_start, U_func, f, g);
    integral_term3 = integral(integrand_term3, t_start, t, ...
                              'RelTol', 1e-6, 'AbsTol', 1e-9, 'ArrayValued', true);
    term3_Z1 = 2 * integral_term3;

    Z1 = X1 + term2_Z1 + term3_Z1;
end

%% Helper functions

function val = exp_integral_to_t(theta, t, U_func, f)
    n = length(theta);
    val = zeros(size(theta));
    for k = 1:n
        if theta(k) < t
            val(k) = exp(integral(@(s) f(U_func(s)), theta(k), t, ...
                                  'RelTol', 1e-6, 'AbsTol', 1e-9));
        else
            val(k) = 1;
        end
    end
end

function val = exp_integral_from_tD(theta, t_start, U_func, f)
    n = length(theta);
    val = zeros(size(theta));
    for k = 1:n
        if theta(k) > t_start
            val(k) = exp(integral(@(s) f(U_func(s)), t_start, theta(k), ...
                                  'RelTol', 1e-6, 'AbsTol', 1e-9));
        else
            val(k) = 1;
        end
    end
end

function val = inner_integral_Z1(theta, t_start, U_func, f, g)
    n = length(theta);
    val = zeros(size(theta));
    for k = 1:n
        if theta(k) > t_start
            integrand = @(s) exp_integral_s_to_theta(s, theta(k), U_func, f) .* g(U_func(s));
            val(k) = integral(integrand, t_start, theta(k), ...
                              'RelTol', 1e-6, 'AbsTol', 1e-9, 'ArrayValued', true);
        end
    end
end

function val = exp_integral_s_to_theta(s, theta, U_func, f)
    n = length(s);
    val = zeros(size(s));
    for k = 1:n
        if s(k) < theta
            val(k) = exp(integral(@(r) f(U_func(r)), s(k), theta, ...
                                  'RelTol', 1e-6, 'AbsTol', 1e-9));
        else
            val(k) = 1;
        end
    end
end
