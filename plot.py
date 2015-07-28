#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create plots from the UNH-RVAT 2-D OpenFOAM case.
"""
from modules import processing, plotting
import matplotlib.pyplot as plt
from pxl.styleplot import set_sns
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plotting results")
    parser.add_argument("plots", nargs="*", default="perf", help="What to plot")
    parser.add_argument("--style", "-S", help="Matplotlib style sheet")
    parser.add_argument("--save", "-s", action="store_true", help="Save plots")
    parser.add_argument("--noshow", action="store_true", default=False, help="Do not show")
    args = parser.parse_args()
    
    if args.style is not None:
        plotting.plt.style.use(args.style)
    else:
        set_sns()
        plotting.plt.rcParams["axes.grid"] = True
        
    if "perf" in args.plots:
        processing.calc_perf(plot=not args.noshow, inertial=False)
    if "wake" in args.plots:
        plotting.plot_u(save=args.save)
        plotting.plot_k(save=args.save)
        
    if not args.noshow:
        plt.show()
