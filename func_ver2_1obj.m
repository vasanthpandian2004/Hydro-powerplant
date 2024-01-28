function [f] = func_ver2_1obj(x)

n = 0.75; %efficiency
p = 998; %density of water
g = 9.81;
h = 110; %head


Q = pi * x(2) * x(1)^2; %turbine flow


f(1) = - (n * p * g * h * Q); %power generated by the turbine

end


