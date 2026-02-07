function dZdt = Z_system_ode(t, Z)
% Z_SYSTEM_ODE Delay-free Z system ODE (Eq. 30-31)
%
% Z system (transformed, no delay):
%   dZ1/dt = 2*Z2 + U
%   dZ2/dt = (Z2 + U) / (U^2 + 1)
%
% Control law (Eq. 32):
%   U = -2*Z2 - Z1

    Z1 = Z(1);
    Z2 = Z(2);

    U = -2*Z2 - Z1;

    dZ1 = 2*Z2 + U;
    dZ2 = (Z2 + U) / (U^2 + 1);

    dZdt = [dZ1; dZ2];
end
