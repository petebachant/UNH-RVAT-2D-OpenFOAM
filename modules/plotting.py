#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plotting functions for the UNH-RVAT-2D OpenFOAM case.
"""
from __future__ import division, print_function
from modules.processing import *


def plot_perf():
    calc_perf(plot=True)
                        
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
        df["steps_per_rev"] = step_per_rev
        x = step_per_rev
        xlab = "Steps per revolution"
    print(df)
    plt.figure()
    plt.plot(x, df.cp, "ok")
    plt.xlabel(xlab, fontsize=16)
    plt.ylabel("$C_P$", fontsize=16)
    plt.grid(True)
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

def plot_u(save=False, savedir="./figures", savetype=".pdf"):
    """Plot mean streamwise velocity profile."""
    timedirs = os.listdir("postProcessing/sets")
    latest_time = max(timedirs)
    data = np.loadtxt(os.path.join("postProcessing", "sets", latest_time,
                      "profile_UMean.xy"), unpack=True)
    u = data[1]
    y_R = data[0]/R
    plt.figure()
    plt.plot(y_R, u, "k", label="SA (2-D)")
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$U$")
    plt.grid(True)
    plt.tight_layout()
    if save:
        if not os.path.isdir(savedir):
            os.makedirs(savedir)
        plt.savefig(os.path.join(savedir, "u_profile_SA" + savetype))

def plot_k(save=False):
    """
    Plot turbulence kinetic energy profile--not applicable for
    Spalart--Allmaras turbulence model."""
    print("Turbulence kinetic energy is zero for Spalart--Allmaras turbulence"
          " model")
          

