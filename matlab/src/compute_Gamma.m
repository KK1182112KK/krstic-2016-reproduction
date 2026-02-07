function Gamma = compute_Gamma(t, X, U_history, D)
% COMPUTE_GAMMA Compute Theorem 1 stability indicator
%
% Gamma(t) = |X(t)| + sup_{t-D <= theta <= t} |U(theta)|
%
% Inputs:
%   t         - Time vector (n x 1)
%   X         - State matrix (n x 2)
%   U_history - Control input history (n x 1)
%   D         - Delay time
%
% Output:
%   Gamma - Indicator values (n x 1)

    n = length(t);
    Gamma = zeros(n, 1);

    for k = 1:n
        X_norm = norm(X(k,:));

        t_current = t(k);
        idx_window = find(t >= t_current - D & t <= t_current);
        if isempty(idx_window)
            U_sup = abs(U_history(k));
        else
            U_sup = max(abs(U_history(idx_window)));
        end

        Gamma(k) = X_norm + U_sup;
    end
end
