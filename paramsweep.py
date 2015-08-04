#!/usr/bin/env python
"""
This script runs multiple simulations to check sensitivity to parameters.

"""
from subprocess import call
import foampy
import os
from modules import processing
import pandas as pd

def set_blockmesh_resolution(nx):
    newres = nx
    resline = "({res} {res} 1)".format(res=newres)
    blocks = """blocks
(
    hex (0 1 2 3 4 5 6 7)
    {}
    simpleGrading (1 1 1)
);
""".format(resline)
    zres = 110.0/float(newres)*0.025
    vertices = """vertices
(
    ( 2.16 -1.83 -{z}) // 0
    ( 2.16  1.83 -{z}) // 1
    (-1.50  1.83 -{z}) // 2
    (-1.50 -1.83 -{z}) // 3
    ( 2.16 -1.83  {z}) // 4
    ( 2.16  1.83  {z}) // 5
    (-1.50  1.83  {z}) // 6
    (-1.50 -1.83  {z}) // 7 
);
""".format(z=zres)
    foampy.dictionaries.replace_value("constant/polyMesh/blockMeshDict", 
                                      "blocks", blocks)
    foampy.dictionaries.replace_value("constant/polyMesh/blockMeshDict", 
                                      "vertices", vertices)
                                      
def set_timestep(dt):
    dt = str(dt)
    foampy.dictionaries.replace_value("system/controlDict", "deltaT", dt)
    
def set_maxco(maxco):
    maxco = str(maxco)
    foampy.dictionaries.replace_value("system/controlDict", "maxCo", maxco)

def spatial_grid_dep(newfile=True, nx_list=range(30, 95, 5)):
    if newfile:
        try:
            os.remove("processed/spatial_grid_dep.csv")
        except OSError:
            pass
    for nx in nx_list:
        call("./Allclean")
        print("Setting blockMesh nX to {}".format(nx))
        set_blockmesh_resolution(nx)
        call("./Allrun")
        processing.log_perf("spatial_grid_dep.csv", verbose=False)
        
def timestep_dep(newfile=True):
    if newfile:
        try:
            os.remove("processed/timestep_dep.csv")
        except OSError:
            pass
    dt_list = [0.004, 
               0.003,
               0.0025,
               0.00225,
               0.002,
               0.00175,
               0.0015,
               0.001, 
               8e-4]
    call("scripts/Allrun.pre")
    for dt in dt_list:
        call("scripts/Allclean.nomesh")
        print("Setting timestep to {}".format(dt))
        set_timestep(dt)
        call("scripts/Allrun.postmesh")
        processing.log_perf("timestep_dep.csv", verbose=False)
        
def maxco_dep(newfile=True):
    if newfile:
        try:
            os.remove("processed/maxco_dep.csv")
        except OSError:
            pass
    maxco_list = [40, 20, 10, 5, 2, 0.9, 0.5]
    call("scripts/Allrun.pre")
    for maxco in maxco_list:
        call("scripts/Allclean.nomesh")
        print("Setting maxCo to {}".format(maxco))
        set_maxco(maxco)
        call("scripts/Allrun.postmesh")
        processing.log_perf("maxco_dep.csv", verbose=False)

def tsr_dep(newfile=True):
    set_timestep(0.002)
    set_blockmesh_resolution(70)
    if newfile:
        try:
            os.remove("processed/tsr_dep.csv")
        except OSError:
            pass
    tsr_list = [3.25, 2.75, 2.25, 1.75, 1.25, 0.75, 0.5]
    call("scripts/Allrun.pre")
    for tsr in tsr_list:
        call("scripts/Allclean.nomesh")
        print("Setting tip speed ratio to {}".format(tsr))
        call("scripts/Allrun.postmesh {}".format(tsr), shell=True)
        processing.log_perf("tsr_dep.csv", verbose=False)
                            
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run parameter variations")
    parser.add_argument("variable", help="Which parameter to vary",
                        choices=["space", "time", "tsr"])
    parser.add_argument("--append", "-a", action="store_true", default=False,
                        help="Append to existing CSV log file")
    args = parser.parse_args()
    
    if args.variable == "space":
        spatial_grid_dep(newfile=not args.append)
    elif args.variable == "time":
        timestep_dep(newfile=not args.append)
    elif args.variable == "tsr":
        tsr_dep(newfile=not args.append)
    
