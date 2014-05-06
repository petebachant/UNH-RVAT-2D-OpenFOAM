UNH RVAT 2D OpenFOAM RANS Case
==============================
OpenFOAM (2.3.0) case files for a 2D RANS simulation of the UNH-RVAT cross-flow turbine in a towing tank. The simulation uses the `pimpleDyMFoam` solver and the `kOmegaSST` turbulence model. 

Note that this simulation has not been verified or validated.

Python scripts
--------------
There are some Python scripts included to perform various tasks. Note that these require `foampy`,
which is an unreleased module in progress.

  * `perf.py` -- calculates performance of turbine, plots torque.
  * `gendynmeshdict.py` -- generates a dynamicMeshDict to rotate the turbine. Note that by defaults the turbine
                     rotates at an angular velocity that is slightly unsteady to match experiments.
  * `prog.py` -- creates a progress bar using PyQt.

Video
-----
A video of the vorticity contours produced by this simulation 
(commit 5aee960afcda71cc3398a6f417780fd3d5e978ba, OpenFOAM version 2.2.2) can be found here:
http://youtu.be/AQ4EztjPEFk

Acknowledgements
----------------
Thanks to Boloar from the cfd-online forums for providing a nice example case on which to base this one. Also thanks to vkrastev for additional advice.

