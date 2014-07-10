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
    newres = "(110 110 1)"
    
blocks = """blocks
(
    hex (0 1 2 3 4 5 6 7)
    {}
    simpleGrading (1 1 1)
);\n""".format(newres)

foampy.dictionaries.replace_value("constant/polyMesh/blockMeshDict", 
                                  "blocks", blocks)
