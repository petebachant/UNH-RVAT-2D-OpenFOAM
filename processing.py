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
import pandas as pd
from pxl import styleplot


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
    
def get_ddt_scheme():
    block = foampy.dictionaries.read_text("system/fvSchemes", 
                                          "ddtSchemes")
    val = block[2].replace(";", "").split()[1]
    return val
    
def get_max_courant_no():
    if foampy.dictionaries.read_single_line_value("controlDict", 
                                                  "adjustTimeStep",
                                                  valtype=str) == "yes":
        return foampy.dictionaries.read_single_line_value("controlDict", 
                                                          "maxCo")
    else:
        return "nan"
        
def get_deltat():
    if foampy.dictionaries.read_single_line_value("controlDict", 
                                                  "adjustTimeStep",
                                                  valtype=str) == "no":
        return foampy.dictionaries.read_single_line_value("controlDict", 
                                                          "deltaT")
    else:
        return "nan"

def calc_perf(plot=False, verbose=True):
    t, torque, drag = foampy.load_all_torque_drag()
    _t, theta, omega = foampy.load_theta_omega(t_interp=t)
    # Compute tip speed ratio
    tsr = omega*R/U_infty
    # Pick an index to start from for mean calculations and plotting
    # (allow turbine to reach steady state)
    try:
        i = np.where(np.round(theta) == 360)[0][0]
    except IndexError:
        print("Target index not found")
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
    if i != 5:
        return {"C_P" : meancp, 
                "C_D" : meancd, 
                "TSR" : meantsr}
    else:
        return {"C_P" : "nan", 
                "C_D" : "nan", 
                "TSR" : "nan"}
            
def log_perf(logname="all_perf.csv", mode="a", verbose=True):
    """Logs mean performance calculations to CSV file. If file exists, data
    is appended."""
    if not os.path.isdir("processed"):
        os.mkdir("processed")
    with open("processed/" + logname, mode) as f:
        if os.stat("processed/" + logname).st_size == 0:
            f.write("dt,maxco,nx,ncells,tsr,cp,cd,yplus_min,yplus_max,yplus_mean,ddt_scheme\n")
        data = calc_perf(verbose=verbose)
        ncells = get_ncells()
        yplus = get_yplus()
        nx = get_nx()
        maxco = get_max_courant_no()
        dt = get_deltat()
        ddt_scheme = get_ddt_scheme()
        f.write("{dt},{maxco},{nx},{ncells},{tsr},{cp},{cd},{ypmin},{ypmax},{ypmean},{ddt_scheme}\n"\
                .format(dt=dt,
                        maxco=maxco,
                        nx=nx,
                        ncells=ncells,
                        tsr=data["TSR"],
                        cp=data["C_P"],
                        cd=data["C_D"],
                        ypmin=yplus["min"],
                        ypmax=yplus["max"],
                        ypmean=yplus["mean"],
                        ddt_scheme=ddt_scheme))
                        
def plot_grid_dep(var="nx", show=True):
    df = pd.read_csv("processed/timestep_dep.csv")
    if var=="maxCo":
        df = df[df.nx==95]
        df = df[~np.isnan(df.maxco)]
        df = df[df.ddt_scheme=="Euler"]
        x = df.maxco
        xlab = r"$Co_\max$"
    elif var == "nx":
        df = df[7:15]
        x = df.nx
        xlab = "$N_x$"
    elif var=="deltaT":
        df = df[np.isnan(df.maxco)]
        x = df.dt
        xlab = r"$\Delta t$"
    elif var=="stepsPerRev":
        tsr = 1.9
        omega = tsr*U_infty/R
        rev_per_sec = omega/(2*np.pi)
        df = df[np.isnan(df.maxco)]
        sec_per_step = df.dt
        step_per_rev = sec_per_step**(-1)*rev_per_sec**(-1)
        x = step_per_rev
        xlab = "Steps per revolution"
    print(df)
    plt.figure()
    plt.plot(x, df.cp, "ok")
    plt.xlabel(xlab, fontsize=16)
    plt.ylabel("$C_P$", fontsize=16)
    if show:
        plt.show()
        
def plot_perf_curve(show=True, save=False, savepath="./", savetype=".pdf"):
    """Plots the performance curve read from processed/tsr_dep.csv."""
    df = pd.read_csv("processed/tsr_dep.csv")
    plt.figure(figsize=(8,3))
    plt.subplot(1, 2, 1)
    plt.plot(df.tsr, df.cp, "ok")
    plt.xlim((0,None))
    plt.xlabel(r"$\lambda$", fontsize=16)
    plt.ylabel(r"$C_P$", fontsize=16)
    plt.subplot(1, 2, 2)
    plt.plot(df.tsr, df.cd, "ok")
    plt.xlim((0,None))
    plt.ylim((0,2))
    plt.xlabel(r"$\lambda$", fontsize=16)
    plt.ylabel(r"$C_D$", fontsize=16)
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(savepath, "perf_curves") + savetype)
    if show:
        plt.show()

if __name__ == "__main__":
#    plot_grid_dep("deltaT", show=True)
    plot_perf_curve()
    
