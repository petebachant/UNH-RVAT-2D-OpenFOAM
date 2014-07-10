#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Processing functions for the UNH-RVAT-2D OpenFOAM case.

"""
from __future__ import division, print_function
import matplotlib.pyplot as plt
import numpy as np 
import foampy
import sys

area = 0.05
R = 0.5
U_infty = 1.0

calc_perf(plot=False):
    t, torque, drag = foampy.load_all_torque_drag()
    _t, theta, omega = foampy.load_theta_omega(t_interp=t) 
    # Compute tip speed ratio
    tsr = omega*R/U_infty
    meantsr = np.mean(tsr)
    print("Mean tsr:", meantsr)
    # Pick an index to start from for mean calculations and plotting
    # (allow turbine to reach steady state)
    try:
        i = np.where(np.round(theta) == 361)[0][0]
    except IndexError:
        i = 5
    i2 = -1
    # Compute power coefficient
    area = 0.05
    power = torque*omega
    cp = power/(0.5*1000*area*1**3)
    meancp = np.mean(cp[i:i2])
    print("Mean cp:", meancp)
    # Compute drag coefficient
    cd = drag/(0.5*1000*area*1**2)
    meancd = np.mean(cd[i:i2])
    print("Mean cd:", meancd)
    if plot:
        plt.close('all')
        plt.plot(theta[i:i2], cp[i:i2])
        plt.title(r"$\lambda = %1.1f$" %meantsr)
        plt.xlabel(r"$\theta$ (degrees)")
        plt.ylabel(r"$C_P$")
        #plt.ylim((0, 1.0))
        plt.show()
    return {"C_P" : meancp, 
            "C_D" : meancd, 
            "TSR" : meantsr}
            
if __name__ == "__main__":
    calc_perf(plot=True)
    