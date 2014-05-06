#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script refines the wall layer
"""
import subprocess
import numpy as np

nlayers = 20
expansion_ratio = 1.25
patches = ["shaft", "blades"]

c = [1]
for n in range(nlayers - 1):
    c.append(expansion_ratio*c[n])
c = np.asarray(c)
c = c/c.sum()

s = [np.sum(c[0:-1])]
for n in range(1, nlayers-1):
    s.append(np.sum(c[0:-n-1])/np.sum(c[0:-n]))

for ratio in s:
    for patch in patches:
        cm = "refineWallLayer -overwrite " + patch + " " + str(ratio)
        print(cm)
        #subprocess.call(cm, shell=True)
