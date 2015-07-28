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

def plot_u(newfig=True, save=False, savedir="figures", savetype=".pdf"):
    """Plot mean streamwise velocity profile."""
    df = load_u_profile()
    if newfig:
        plt.figure()
    plt.plot(df.y_R, df.u, "k", label="SA (2-D)")
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$U$")
    plt.grid(True)
    plt.tight_layout()
    if save:
        if not os.path.isdir(savedir):
            os.makedirs(savedir)
        plt.savefig(os.path.join(savedir, "u_profile_SA" + savetype))

def plot_k(amount="total", newfig=True, save=False):
    """Plot turbulence kinetic energy profile."""
    timedirs = os.listdir("postProcessing/sets")
    latest_time = max(timedirs)
    if amount == "total" or amount == "resolved":
        data = np.loadtxt(os.path.join("postProcessing", "sets", latest_time,
                          "profile_UPrime2Mean.xy"), unpack=True)
        k = 0.5*(data[1] + data[4] + data[6])
    if amount == "modeled" or amount == "total":
        data = np.loadtxt(os.path.join("postProcessing", "sets", latest_time,
                          "profile_kMean.xy"), unpack=True)
        kmod = data[1]
        if amount == "modeled":
            k = kmod
        elif amount == "total":
            k += kmod
    y_R = data[0]/R
    if newfig:
        plt.figure()
    plt.plot(y_R, k/U_infty**2, "k", label="SA (2-D)")
    plt.xlabel(r"$y/R$")
    plt.ylabel(r"$k/U_\infty^2$")
    plt.grid(True)
    plt.tight_layout()
    if save:
        if not os.path.isdir(savedir):
            os.makedirs(savedir)
        plt.savefig(os.path.join(savedir, "k_{}_profile_SA{}".format(
                amount, savetype)))
          
def make_momentum_trans_bargraph(print_analysis=True):
    data = read_funky_log()
    y_adv = data["y_adv"]
    z_adv = data["z_adv"]
    turb_trans = data["turb_trans"]
    visc_trans = data["visc_trans"]
    pressure_trans = data["pressure_trans"]
    plt.figure(figsize=(7.5, 4))
    ax = plt.gca()
    ax.bar(range(5), [y_adv, z_adv, turb_trans, visc_trans, pressure_trans], 
           color="gray", edgecolor="black", width=0.5)
    ax.set_xticks(np.arange(5)+0.25)
    ax.set_xticklabels(["$y$-adv.", "$z$-adv.",
                        "Turb.", "Visc.", "Press."])
    plt.ylabel(r"$\frac{U \, \mathrm{ transport}}{UDU_\infty}$")
    plt.tight_layout()
    if print_analysis:
        sum = y_adv + z_adv + turb_trans + visc_trans + pressure_trans
        print("Momentum recovery = {:.3f}% per turbine diameter".format(sum))
    plt.show()

def plot_mom_transport(show=True):
    df = pd.read_csv("processed/mom_transport.csv")
    print(df)
    plt.plot(df.x, df.y_adv, "-o", label=r"$-V \partial U / \partial y$")
    plt.plot(df.x, df.z_adv, "-s", label=r"$-W \partial U / \partial z$")
    plt.plot(df.x, df.turb_trans, "-^", label=r"$\nu_t \nabla^2 U$")
    plt.plot(df.x, df.visc_trans, "->", label=r"$\nu \nabla^2 U$")
    plt.plot(df.x, df.pressure_trans/10, "-<", label=r"$-\partial P / \partial x$ ($\times 10^{-1}$)")
    plt.legend(loc=4)
    plt.xlabel("$x/D$")
    plt.ylabel(r"$\frac{U \, \mathrm{ transport}}{UU_\infty D^{-1}}$")
    plt.grid()
    plt.tight_layout()
    if show:
        plt.show()

def plot_U_streamwise(show=True):
    times = os.listdir("postProcessing/sets")
    times.sort()
    latest = times[-1]
    filepath = os.path.join("postProcessing", "sets", latest, 
                            "streamwise_U.xy")
    x, u, v, w = np.loadtxt(filepath, unpack=True)
    plt.plot(x, u, "k")
    plt.xlabel("$x/D$")
    plt.ylabel(r"$U/U_\infty$")
    plt.grid()
    plt.tight_layout()
    if show:
        plt.show()

def plot_streamwise(save=False, savepath=""):
    plt.figure(figsize=(12,5))
    plt.subplot(121)
    plot_U_streamwise(show=False)
    plt.subplot(122)
    plot_mom_transport(show=False)
    if save:
        plt.savefig(os.path.join(savepath, "AD_streamwise.pdf"))
    plt.show()
