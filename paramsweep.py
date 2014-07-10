#!/usr/bin/env python
"""
This script runs multiple simulations to check sensitivity to parameters.

"""
from subprocess import call
import foampy
import os
import processing
import pandas as pd

def set_blockmesh_resolution(nx)
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

def spatial_grid_dep():
    grids = [50, 80, 110, 140]
    cp = []
    cd = []
    tsr = []
    for grid in grids:
        set_blockmesh_resolution(grid)
        call("./Allrun")
        data = processing.calc_perf()
        cp.append(data["C_P"])
        cd.append(data["C_D"])
        tsr.append(data["TSR"])
        call("./Allclean")
    if not os.path.isdir("processed"):
        os.mkdir("processed")
    pd.DataFrame({"nx" : grids, 
                  "C_P", cp, 
                  "C_D", cd,
                  "TSR", tsr}).to_csv("processed/spatial_grid_dep.csv")
      
def main():
    spatial_grid_dep()
                            
if __name__ == "__main__":
    main()

