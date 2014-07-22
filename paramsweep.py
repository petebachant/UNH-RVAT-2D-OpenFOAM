#!/usr/bin/env python
"""
This script runs multiple simulations to check sensitivity to parameters.

"""
from subprocess import call
import foampy
import os
import processing
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
    (-1.52  1.83 -{z}) // 2
    (-1.52 -1.83 -{z}) // 3
    ( 2.16 -1.83  {z}) // 4
    ( 2.16  1.83  {z}) // 5
    (-1.52  1.83  {z}) // 6
    (-1.52 -1.83  {z}) // 7 
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

def spatial_grid_dep():
    call("rm -f processed/spatial_grid_dep.csv", shell=True)
    nx_list = [35, 45, 55, 70, 85]
    for nx in nx_list:
        call("./Allclean")
        set_blockmesh_resolution(nx)
        call("./Allrun")
        processing.log_perf("spatial_grid_dep.csv", verbose=False)
        
def timestep_dep():
    call("rm -f processed/timestep_dep.csv", shell=True)
    dt_list = [6e-3, 4e-3, 3e-3, 2.5e-3, 2e-3, 1.5e-3, 1e-3, 7e-4, 5e-4]
    call("./Allrun.pre")
    for dt in dt_list:
        call("./Allclean.nomesh")
        print("Setting timestep to {}".format(dt))
        set_timestep(dt)
        call("./Allrun.postmesh")
        processing.log_perf("timestep_dep.csv", verbose=False)
        
def maxco_dep():
    call("rm -f processed/maxco_dep.csv", shell=True)
    maxco_list = [100, 80, 60, 40, 20, 10, 5, 2]
    call("./Allrun.pre")
    for maxco in maxco_list:
        call("./Allclean.nomesh")
        print("Setting maxCo to {}".format(maxco))
        set_maxco(maxco)
        call("./Allrun.postmesh")
        processing.log_perf("maxco_dep.csv", verbose=False)
                            
if __name__ == "__main__":
    timestep_dep()
