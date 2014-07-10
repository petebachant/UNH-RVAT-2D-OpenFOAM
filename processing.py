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
import os

area = 0.05
R = 0.5
U_infty = 1.0
rho = 1000.0

def get_ncells(logname="log.checkMesh", keyword="cells"):
    if keyword == "cells":
        keyword = "cells:"
    with open(logname) as f:
        for line in f.readlines():
            ls = line.split()
            if ls and ls[0] == keyword:
                value = ls[1]
                return int(value)
                
def get_yplus(logname="log.yPlus"):
    with open(logname) as f:
        lines = f.readlines()
        for n in range(len(lines)):
            ls = lines[n].split()
            if ls and ls[-1] == "blades":
                nstart = n
                break
    line = lines[n+3]
    line = line.split()
    return {"min" : float(line[3]),
            "max" : float(line[5]),
            "mean" : float(line[7])}
            
def get_nx():
    blocks = foampy.dictionaries.read_text("constant/polyMesh/blockMeshDict", 
                                           "blocks")
    nx = int(blocks[3].replace("(", "").split()[0])
    return nx

def calc_perf(plot=False, verbose=True):
    t, torque, drag = foampy.load_all_torque_drag()
    _t, theta, omega = foampy.load_theta_omega(t_interp=t)
    # Compute tip speed ratio
    tsr = omega*R/U_infty
    # Pick an index to start from for mean calculations and plotting
    # (allow turbine to reach steady state)
    try:
        i = np.where(np.round(theta) == 361)[0][0]
    except IndexError:
        i = 5
    i2 = -1
    # Compute mean TSR
    meantsr = np.mean(tsr[i:i2])
    # Compute power coefficient
    power = torque*omega
    cp = power/(0.5*rho*area*U_infty**3)
    meancp = np.mean(cp[i:i2])
    # Compute drag coefficient
    cd = drag/(0.5*rho*area*U_infty**2)
    meancd = np.mean(cd[i:i2])
    if verbose:
        print("Mean TSR =", meantsr)
        print("Mean C_P =", meancp)
        print("Mean C_D =", meancd)
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
            
def log_perf(logname="all_perf.csv", mode="a", verbose=True):
    """Logs mean performance calculations to CSV file. If file exists, data
    is appended."""
    if not os.path.isdir("processed"):
        os.mkdir("processed")
    with open("processed/" + logname, mode) as f:
        if os.stat("processed/" + logname).st_size == 0:
            f.write("nx,ncells,tsr,cp,cd,yplus_min,yplus_max,yplus_mean\n")
        data = calc_perf(verbose=verbose)
        ncells = get_ncells()
        yplus = get_yplus()
        nx = get_nx()
        f.write("{nx},{ncells},{tsr},{cp},{cd},{ypmin},{ypmax},{ypmean}\n"\
                .format(nx=nx,
                        ncells=ncells,
                        tsr=data["TSR"],
                        cp=data["C_P"],
                        cd=data["C_D"],
                        ypmin=yplus["min"],
                        ypmax=yplus["max"],
                        ypmean=yplus["mean"])) 

if __name__ == "__main__":
    get_nx()
    calc_perf(plot=False)
    
