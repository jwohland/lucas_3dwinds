# lucas_3dwinds

Analysis of land-use change impacts on 3d wind fields. 

Initial leading questions:
1. What is the magnitude of potential wind speed changes on different height levels?
2. Is there convergence of the wind fields from different extreme simulations at a certain height? Or: Does the lower boundary conditions affect winds even far above ground (say 1km +)?
3. What is the impact on stability and air density at different heights?

This is a collaborative project. Please feel free to add to the discussion by replying to issues or opening new issues.

The `data` folder is structured as

> institution/experiment/variable/*.nc

where institution is one of [GERICS, OUR, ETH, JLU, IDL] 
and experiment is one of [EVAL, FOREST, GRASS].

Jupyter Notebooks in 

> notebooks

are used for testing and as a playground. They are not part of the proper analysis.