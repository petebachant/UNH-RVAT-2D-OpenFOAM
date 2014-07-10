#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script replaces a value in the blockMeshDict
"""

import foampy
import sys

if len(sys.argv) > 1:
    newres = sys.argv[1]
else:
    newres = 110
    
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
