function U_val = interp_control_history(s, t_U0, U0, t_sim, U_sim)
% INTERP_CONTROL_HISTORY Unified interpolation of control input history
%
% Handles the transition between three regimes:
%   1. Before history:  s < t_U0(1)     -> return 0
%   2. History period:  t_U0(1) <= s <= 0 -> interpolate from (t_U0, U0)
%   3. Simulation:      0 < s <= t_sim(end) -> interpolate from (t_sim, U_sim)
%   4. Beyond data:     s > t_sim(end)  -> hold last value
%
% Supports both scalar and vector inputs for s.
%
% Inputs:
%   s      - Query time(s) (scalar or vector)
%   t_U0   - Initial history time grid (t <= 0)
%   U0     - Initial history values
%   t_sim  - Simulation time grid (t >= 0)
%   U_sim  - Simulation control values
%
% Output:
%   U_val  - Interpolated control value(s), same size as s

    U_val = zeros(size(s));

    for k = 1:numel(s)
        sk = s(k);
        if sk < t_U0(1)
            U_val(k) = 0;
        elseif sk <= 0
            U_val(k) = interp1(t_U0, U0, sk, 'linear', 0);
        elseif sk <= t_sim(end)
            U_val(k) = interp1(t_sim, U_sim, sk, 'linear', 'extrap');
        else
            U_val(k) = U_sim(end);
        end
    end
end
