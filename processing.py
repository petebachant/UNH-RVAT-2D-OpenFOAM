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
from pxl import fdiff

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

def calc_perf(theta_0=360, plot=False, verbose=True, inertial=False):
    t, torque, drag = foampy.load_all_torque_drag()
    _t, theta, omega = foampy.load_theta_omega(t_interp=t)
    reached_theta_0 = True
    if theta.max() < theta_0:
        theta_0 = 1
        reached_theta_0 = False
    # Compute tip speed ratio
    tsr = omega*R/U_infty
    # Compute mean TSR
    meantsr = np.mean(tsr[theta >= theta_0])
    if inertial:
        inertia = 3 # guess from SolidWorks model
        inertial_torque = inertia*fdiff.second_order_diff(omega, t)
        torque -= inertial_torque
    # Compute power coefficient
    power = torque*omega
    cp = power/(0.5*rho*area*U_infty**3)
    meancp = np.mean(cp[theta >= theta_0])
    # Compute drag coefficient
    cd = drag/(0.5*rho*area*U_infty**2)
    meancd = np.mean(cd[theta >= theta_0])
    if verbose:
        print("Mean TSR =", meantsr)
        print("Mean C_P =", meancp)
        print("Mean C_D =", meancd)
    if plot:
        plt.close('all')
        plt.plot(theta[5:], cp[5:])
        plt.title(r"$\lambda = %1.1f$" %meantsr)
        plt.xlabel(r"$\theta$ (degrees)")
        plt.ylabel(r"$C_P$")
        #plt.ylim((0, 1.0))
        plt.tight_layout()
        plt.show()
    if reached_theta_0:
        return {"C_P" : meancp, 
                "C_D" : meancd, 
                "TSR" : meantsr}
    else:
        return {"C_P" : "nan", 
                "C_D" : "nan", 
                "TSR" : "nan"}
                
def load_set(casedir="", name="profile", quantity="U", fmt="xy", axis="xyz"):
    """Imports text data created with the OpenFOAM sample utility"""
    if casedir != "":
        folder = casedir + "/postProcessing/sets"
    else:
        folder = "postProcessing/sets"
    t = []
    times = os.listdir(folder)
    for time1 in times:
        try: 
            float(time1)
        except ValueError: 
            times.remove(time1)
        try:
            t.append(int(time1))
        except ValueError:
            t.append(float(time1))
    t.sort()
    data = {"time" : t}
    for ts in t:
        filename = "{folder}/{time}/{name}_{q}.{fmt}".format(folder=folder,
            time=ts, name=name, q=quantity, fmt=fmt)
        with open(filename) as f:
            d = np.loadtxt(f)
            if quantity == "U":
                data[ts] = {"u" : d[:, len(axis)],
                            "v" : d[:, len(axis)+1],
                            "w" : d[:, len(axis)+2]}
                if len(axis) == 1:
                    data[ts][axis] = d[:,0]
                else:
                    data[ts]["x"] = d[:,0]
                    data[ts]["y"] = d[:,1]
                    data[ts]["z"] = d[:,2]
    return data
    
def calc_blade_vel():
    """Calculates blade angle of attack and relative velocity time series."""
    # Load sampled data
    data = load_set(name="bladePath", quantity="U")
    times = data["time"]
    # Load turbine azimuthal angle time series
    _t, theta_blade, omega = foampy.load_theta_omega(t_interp=times)
    theta_turbine = theta_blade*1
    theta_blade = theta_blade.round(decimals=0) % 360
    theta_probe = theta_blade + 4
    theta_blade_rad = theta_blade/180*np.pi
    rel_vel = []
    alpha = []
    rel_vel_geom = []
    alpha_geom = []
    # Calculate an array of thetas that correspond to each sampled point
    for i, t in enumerate(times):
        x = data[t]["x"]
        y = data[t]["y"]
        u = data[t]["u"]
        v = data[t]["v"]
        theta = np.round(np.arctan2(-x, y)*180/np.pi, decimals=0)
        theta = [(360 + th) % 360 for th in theta]
        blade_vel_mag = omega[i]*R
        blade_vel_x = blade_vel_mag*np.cos(theta_blade_rad[i])
        blade_vel_y = blade_vel_mag*np.sin(theta_blade_rad[i])
        u_geom = 1.0
        rel_vel_mag_geom = np.sqrt((blade_vel_x + u_geom)**2 + blade_vel_y**2)
        rel_vel_geom.append(rel_vel_mag_geom)
        rel_vel_x_geom = u_geom + blade_vel_x
        rel_vel_y_geom = blade_vel_y
        relvel_dot_bladevel_geom = (blade_vel_x*rel_vel_x_geom + blade_vel_y*rel_vel_y_geom)
        _alpha = np.arccos(relvel_dot_bladevel_geom/(rel_vel_mag_geom*blade_vel_mag))
        alpha_geom.append(_alpha*180/np.pi)
        try:
            ivel = theta.index(theta_probe[i])
            ui = u[ivel]
            vi = v[ivel]
            rel_vel_mag = np.sqrt((blade_vel_x + ui)**2 + (blade_vel_y + vi)**2)
            rel_vel.append(rel_vel_mag)
            rel_vel_x = ui + blade_vel_x
            rel_vel_y = vi + blade_vel_y
            relvel_dot_bladevel = (blade_vel_x*rel_vel_x + blade_vel_y*rel_vel_y)
            _alpha = np.arccos(relvel_dot_bladevel/(rel_vel_mag*blade_vel_mag))
            alpha.append(_alpha*180/np.pi)
        except ValueError:
            rel_vel.append(np.nan)
            alpha.append(np.nan)
    rel_vel = np.array(rel_vel)
    alpha = np.array(alpha)
    alpha[theta_blade > 180] = -alpha[theta_blade > 180]
    rel_vel_geom = np.array(rel_vel_geom)
    alpha_geom = np.array(alpha_geom)
    alpha_geom[theta_blade > 180] = -alpha_geom[theta_blade > 180]
    theta_0 = 720
    alpha = alpha[theta_turbine > theta_0]
    rel_vel = rel_vel[theta_turbine > theta_0]
    alpha_geom = alpha_geom[theta_turbine > theta_0]
    rel_vel_geom = rel_vel_geom[theta_turbine > theta_0]
    theta_turbine = theta_turbine[theta_turbine > theta_0]
    plt.figure(figsize=(8,3))
    plt.subplot(1, 2, 1)
    plt.plot(theta_turbine, alpha, "--ok")
    plt.plot(theta_turbine, alpha_geom)
    plt.xlabel("Azimuthal angle (degrees)")
    plt.ylabel("Angle of attack (degrees)")
    plt.subplot(1, 2, 2)
    plt.plot(theta_turbine, rel_vel, "--ok")
    plt.plot(theta_turbine, rel_vel_geom)
    plt.xlabel("Azimuthal angle (degrees)")
    plt.ylabel("Relative velocity (m/s)")
    plt.tight_layout()
    plt.show()
        
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
    if var=="maxCo":
        df = pd.read_csv("processed/maxco_dep.csv")
        df = df[df.nx==95]
        df = df[~np.isnan(df.maxco)]
        df = df[df.ddt_scheme=="Euler"]
        df = df[np.abs(df.cp) < 1]
        x = df.maxco
        xlab = r"$Co_\max$"
    elif var == "nx":
        df = pd.read_csv("processed/spatial_grid_dep.csv")
        df = df[7:15]
        x = df.nx
        xlab = "$N_x$"
    elif var=="deltaT":
        df = pd.read_csv("processed/timestep_dep.csv")
        df = df[np.isnan(df.maxco)]
        x = df.dt
        xlab = r"$\Delta t$"
    elif var=="stepsPerRev":
        df = pd.read_csv("processed/timestep_dep.csv")
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
    plt.tight_layout()
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
    plot_grid_dep("maxCo", show=True)
#    calc_blade_vel()
