#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 09:22:09 2013

@author: pete
"""

import matplotlib.pyplot as plt
import re
import numpy as np

forceRegex = r"([0-9.eE\-+]+)\s+\(+([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)"
forceRegex += r"\,\(([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)"
forceRegex += r"\,\(([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)+"
forceRegex += r"\s+\(+([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)"
forceRegex += r"\,\(([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)"
forceRegex += r"\,\(([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)+"

t = []
fpx = []; fpy = []; fpz = []
fpox = []; fpoy = []; fpoz = []
fvx = []; fvy = []; fvz = []
mpx = []; mpy = []; mpz = []
mpox = []; mpoy = []; mpoz = []
mvx = []; mvy = []; mvz = []

pipefile = open('postProcessing/forces/0/forces.dat','r')
lines = pipefile.readlines()

for line in lines:
        match = re.search(forceRegex,line)
        if match:
                t.append(float(match.group(1)))
                fpx.append(float(match.group(2)))
                fpy.append(float(match.group(3)))
                fpz.append(float(match.group(4)))
                fvx.append(float(match.group(5)))
                fvy.append(float(match.group(6)))
                fvz.append(float(match.group(7)))
                fpox.append(float(match.group(8)))
                fpoy.append(float(match.group(9)))
                fpoz.append(float(match.group(10)))
                mpx.append(float(match.group(11)))
                mpy.append(float(match.group(12)))
                mpz.append(float(match.group(13)))
                mvx.append(float(match.group(14)))
                mvy.append(float(match.group(15)))
                mvz.append(float(match.group(16)))
                mpox.append(float(match.group(17)))
                mpoy.append(float(match.group(18)))
                mpoz.append(float(match.group(19)))

#Convert to numpy arrays
t = np.asarray(t)
torque = np.asarray(np.asarray(mpz) + np.asarray(mvz))

# Import turbine angular velocity in radians per second
t_omega = []
omega = []
f = open("constant/dynamicMeshDict", "r")
omegaRegex = r"\d+.\d+"
for line in f.readlines():
    match = re.findall(omegaRegex, line)
    if len(match)==2:
        t_omega.append(float(match[0]))
        omega.append(float(match[1]))
f.close()
omega_b = np.asarray(omega)
t_omega = np.asarray(t_omega)
meanomega = np.mean(omega)

# Interpolate omega to match t vector
omega = np.interp(t, t_omega, omega_b)

# create a theta (deg) vector
amp_omega = np.max(omega) - meanomega
theta = meanomega*t - amp_omega/(meanomega*3)*np.cos(3*meanomega*t - np.pi/1.2)
theta = theta/np.pi*180

# Compute tip speed ratio
R = 0.5
U = 1.0
tsr = meanomega*R/U
rpm = omega/(2*np.pi)*60
print "Mean tsr:", tsr

# Pick an index to start from for mean calculations and plotting
# (allow turbine to reach steady state)
i = np.where(np.round(theta) == 360)[0][0]
i2 = -1

# Compute power coefficient
area = 1.0*0.05
power = torque*omega
cp = power/(0.5*1000*area*1**3)
print "Mean cp:", np.mean(cp[i:i2])

# Compute drag coefficient
drag = np.asarray(np.asarray(fpx) + np.asarray(fvx))
cd = drag/(0.5*1000*area*1**2)
print "Mean cd:", np.mean(cd[i:i2])

plt.close('all')
plt.plot(theta[i:i2], torque[i:i2])
plt.title(r"Torque at $\lambda = %1.1f$" %tsr)
plt.xlabel(r"$\theta$ (degrees)")
plt.ylabel("Torque (Nm)")
plt.show()
