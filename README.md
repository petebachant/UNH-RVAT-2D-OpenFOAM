unh-rvat-2d-rans
================
OpenFOAM (2.2.2) case files for a 2D RANS simulation of the UNH-RVAT cross-flow turbine in a towing tank. The simulation uses the `pimpleDyMFoam` solver and the `kOmegaSST` turbulence model. 

Note that this simulation has not been verified or validated.

Thanks to Boloar from the cfd-online forums for providing a nice example case to modify. 

Python scripts
--------------
There are some Python scripts included to perform various tasks:

  * `calcperf.py` -- calculates performance of turbine, plots torque.
  * `gendynmeshdict.py` -- generates a dynamicMeshDict to rotate the turbine. Note that by defaults the turbine
                     rotates at an angular velocity that is slightly unsteady to match experiments.
  * `send_email.py` -- can be customized to send an email when the simulation finishes.
  * `qtprog.py` -- creates a progress bar using PyQt.

Video
-----
A video of the vorticity contours produced by this simulation can be found here:
http://youtu.be/AQ4EztjPEFk
