# Hydropower-Optimization-Project

The goal is to maximize the power generated in a dam while keeping a minimum river flow for wildlife preservation. The algorithms used are fminsearch, patternsearch, PSwarm, evolutionary algorithm, ga (genetic algorithm) and gamultiobj.
The full objective function and restrictions associated to the problem were only used with the genetic algorithm for the others, adaptations were made.
It was concluded that the most adequate solver for the problem is a multiobjective genetic algorithm.


## Objective function

max (−η∗ρ∗π∗x_1^2 ∗x_2 ∗g∗∆h)<br/>
min (π∗x_3^2 ∗x_2 )

x_1 is the turbine's tube radius in meters<br/>
x_2 is the water's velocity in m/s<br/>
x_3 is the spillway's tube radius in meters

## Constraints

0 ≤x_1 ≤ 3<br/>
6 ≤x_2 ≤ 20<br/>
0 ≤x_3 ≤ 5<br/>
π∗x_1^2 ∗x_2 ≥ 400<br/>
π∗x_1^2 ∗x_2 +π∗x_3^2 ∗x_2 ≥ 400<br/>
0.7∗V_init≤V_i≤ 55E6<br/>
