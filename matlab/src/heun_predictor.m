function [Z1, Z2, p1_all, p2_all] = heun_predictor(X1, X2, u, D, N)
% HEUN_PREDICTOR Compute predictor states via spatial Heun integration
%
% Solves the Type II predictor spatial ODE (Eq. 79-80 in the paper):
%   dp2/dx = (p2 + u(x)) / (u(x)^2 + 1),   p2(0) = X2
%   dp1/dx = 2*p2,                           p1(0) = X1
%
% Uses the Heun method (explicit trapezoid, O(dx^2)) over x in [0, D].
%
% Inputs:
%   X1, X2  - Plant state (initial conditions for spatial ODE)
%   u       - Actuator state vector (N or N+1 elements)
%             If N elements: boundary u(N+1) is extrapolated from u(N)
%             If N+1 elements: full grid including right boundary
%   D       - Delay time
%   N       - Number of spatial grid intervals
%
% Outputs:
%   Z1, Z2      - Predictor states: Z_j = p_j(D)
%   p1_all       - Full spatial profile p1(x) (N+1 points, optional)
%   p2_all       - Full spatial profile p2(x) (N+1 points, optional)

    dx = D / N;

    % Handle u vector size: extend to N+1 if needed
    if length(u) == N
        u_ext = [u(:); u(end)];  % Extrapolate boundary
    elseif length(u) >= N+1
        u_ext = u(1:N+1);
    else
        error('heun_predictor: u must have at least N=%d elements, got %d.', N, length(u));
    end

    % Preallocate if full profiles requested
    if nargout > 2
        p2_all = zeros(N+1, 1);
        p1_all = zeros(N+1, 1);
        p2_all(1) = X2;
        p1_all(1) = X1;
    end

    p2 = X2;
    p1 = X1;

    for i = 1:N
        u_i   = u_ext(i);
        u_ip1 = u_ext(i+1);

        % Heun method for p2: dp2/dx = (p2 + u) / (u^2 + 1)
        f_p2_i   = (p2 + u_i) / (u_i^2 + 1);
        p2_euler = p2 + dx * f_p2_i;
        f_p2_ip1 = (p2_euler + u_ip1) / (u_ip1^2 + 1);
        p2_new   = p2 + dx/2 * (f_p2_i + f_p2_ip1);

        % Heun method for p1: dp1/dx = 2*p2
        k1_p1  = 2 * p2;
        k2_p1  = 2 * p2_new;
        p1_new = p1 + dx/2 * (k1_p1 + k2_p1);

        p2 = p2_new;
        p1 = p1_new;

        if nargout > 2
            p2_all(i+1) = p2;
            p1_all(i+1) = p1;
        end
    end

    Z1 = p1;
    Z2 = p2;
end
