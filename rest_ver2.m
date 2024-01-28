function [C,Ceq] = rest_ver2(x,Vi)

rng(1);
t = 3600; %delta t in seconds
V_init = 50e6; %https://www.tandfonline.com/doi/pdf/10.1623/hysj.49.5.901.55139?needAccess=true
Q_in = randi([100,1000],1,50); % inflow


Q = pi * x(2) * x(1)^2; %turbine flow

Q_spill = pi * x(2) * x(3)^2; %spill flow

C = [ pi*x(1)^2*x(2)-400 , -(Vi-0.7*V_init) , -(pi*x(2)*x(1)^2+pi*x(2)*x(3)^2-400) , Vi - 55e6];

Ceq = [];

    
end

