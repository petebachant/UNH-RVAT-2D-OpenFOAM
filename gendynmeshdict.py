#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script creates the dynamic mesh dictionary with periodic omega

omega fluctuates with 3 periods per rotation, and a phase shift to put
the first peak at 80 degrees, to match experiments

@author: pete
"""
import sys
import foampy

if len(sys.argv) > 1:
    meantsr = float(sys.argv[1])
else:
    meantsr = 1.9

U = 1.0
R = 0.5

foampy.gen_dynmeshdict(U, R, meantsr, cellzone="AMISurface", npoints=500)
