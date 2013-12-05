#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script creates the dynamic mesh dictionary with periodic omega

omega fluctuates with 3 periods per rotation, and a phase shift to put
the first peak at 80 degrees, to match experiments

@author: pete
"""

import matplotlib.pyplot as plt
import numpy as np
import re


# Read endTime for simulation
def getEndTime():
    """Get run parameters"""
    f = open("system/controlDict", "r")
    for line in f.readlines():
        if "endTime" in line:
            endTime = re.findall("\d.\d+", line)
            if endTime == []:
                endTime = re.findall("\d+", line)
    f.close()
    endTime = np.float(endTime[0])
    return endTime

# Input parameters -- should probably make these args
U = 1.0
R = 0.5
meantsr = 1.9
meanomega = meantsr*U/R
amp_omega = 3.7*2*np.pi/60.0 # amplitude of fluctuation is 3.7 RPM
endTime = getEndTime()
t = np.linspace(0, endTime, 400)
omega = meanomega + amp_omega*np.sin(3*meanomega*t - np.pi/1.2)

# Write to file
top = """\
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.2.2                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      dynamicMeshDict;
}


dynamicFvMesh   solidBodyMotionFvMesh;

motionSolverLibs ( "libfvMotionSolvers.so" );

solidBodyMotionFvMeshCoeffs
{
    cellZone        AMIsurface_z;

    solidBodyMotionFunction  rotatingMotion;
    rotatingMotionCoeffs
    {
	origin		(0 0 0);
	axis		(0 0 1);
        omega		table
	(
"""

bottom = """
        );
    }
}"""

"""Table should be in form
		(t0 omega0)
		(t1 omega1)
"""

table = ""

for n in xrange(len(t)-1):
    table += "            (" + str(t[n]) + "  " + str(omega[n]) + ")\n"
table += "            (" + str(t[-1]) + "  " + str(omega[-1]) + ")"

alltxt = top + table + bottom


with open("constant/dynamicMeshDict", "w") as f:
    f.write(alltxt)


