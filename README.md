UNH-RVAT 2D OpenFOAM case
=========================

OpenFOAM (2.3.x) case files for a 2D RANS simulation of the UNH-RVAT cross-flow
turbine in a towing tank. The simulation uses the `pimpleDyMFoam` solver and the
`kOmegaSST` turbulence model. 

Note that this simulation has not been verified or validated.

Python scripts
--------------
There are some Python scripts included to perform various tasks. Note that these
require [foamPy](https://github.com/petebachant/foamPy.git).

  * `perf.py` -- calculates performance of turbine, plots torque.
  * `gendynmeshdict.py` -- generates a dynamicMeshDict to rotate the turbine. 
    Note that by default the turbine rotates at an angular velocity that is 
    slightly unsteady to match experiments.
  * `prog.py` -- creates a progress bar using PyQt.

To-do
-----
  * Larger timesteps
  * Higher order time schemes
  
Tagged commits
--------------

### `mesh0`
  * 139k cells
  * Average `yPlus` at 6 s: 2.44 at blades, 0.944 at shaft
  * Mean `C_P` from 360 deg to 6 s: 0.51
  * `maxCo`: 20
  
### `mesh1`
  * 450k cells
  * Average `yPlus` at 6 s: 1.2 at blades
  * `maxCo` = 40
  * `deltaT` ~ 0.002
  * Mean `C_P` from 360 deg to 6 s: 0.54

Video
-----
A video of the vorticity contours produced by this simulation (commit
5aee960afcda71cc3398a6f417780fd3d5e978ba, OpenFOAM version 2.2.2) can be
found here: http://youtu.be/AQ4EztjPEFk

Acknowledgements
----------------
Thanks to Boloar from the cfd-online forums for providing a nice example case on
which to base this one. Also thanks to vkrastev for additional advice.

## License

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/4.0/88x31.png" />
</a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"/>
Creative Commons Attribution 4.0 International License</a>.
