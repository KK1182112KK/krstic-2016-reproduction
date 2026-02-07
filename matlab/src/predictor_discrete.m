function [Z1, Z2, U] = predictor_discrete(X, u, D, N)
% PREDICTOR_DISCRETE Compute predictor states and control input
%
% Thin wrapper around heun_predictor for backward compatibility.
%
% Inputs:
%   X  - Plant state [X1; X2]
%   u  - Actuator state vector (N elements)
%   D  - Delay time
%   N  - Number of spatial grid points
%
% Outputs:
%   Z1, Z2 - Predicted states
%   U      - Control input

    [Z1, Z2] = heun_predictor(X(1), X(2), u, D, N);
    U = -2*Z2 - Z1;
end
