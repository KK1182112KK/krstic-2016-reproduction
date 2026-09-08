function [t_out,X_out,U_out,Z_out] = run_direct_closedloop(D,dt,t_end,X0)
% RUN_DIRECT_CLOSEDLOOP Backward-compatible entry for original-plant simulation.
% The controller is sampled and zero-order held; refine dt to assess this
% implementation's difference from ideal continuous-time feedback.
% Supersedes the former extrapolated-history / held-delayed-input RK4 routine.
    if nargin<1 || isempty(D), D=1; end
    if nargin<2 || isempty(dt), dt=.01; end
    if nargin<3 || isempty(t_end), t_end=20; end
    if nargin<4 || isempty(X0), X0=[1;1]; end
    [t_out,X_out,U_out,Z_out]=run_original_dde(D,dt,t_end,X0);
end
