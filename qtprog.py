#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 21:34:46 2013

@author: pete
"""

import re
import os
import time
import numpy as np
from PyQt4 import QtCore, QtGui


def getParams():
    """Get run parameters"""
    f = open("system/controlDict", "r")
    for line in f.readlines():
        if "endTime" in line:
            endTime = re.findall("\d.\d+", line)
            if endTime == []:
                endTime = re.findall("\d+", line)
        if "writeInterval" in line:
            writeInterval = re.findall("\d.\d+", line)
    f.close()
    endTime = endTime[0]
    writeInterval = writeInterval[0]
    return endTime, writeInterval



class Progress(QtCore.QThread):
    procDone = QtCore.pyqtSignal(bool)
    partDone = QtCore.pyqtSignal(int)
    
    def run(self):
        endTime, writeInterval = getParams()
        done = False
        
        while not done:
            # Find highest valued folder in "processor0" folder
            if os.path.isdir(endTime):
                done = True
                self.partDone.emit(100)
            else:
                dirs = os.listdir("processor0")
                numdirs = np.array([])
                for d in dirs:
                    try:
                        numdirs = np.append(numdirs, float(d))
                    except ValueError:
                        pass
                self.partDone.emit(int(np.max(numdirs)/float(endTime)*100))
            time.sleep(1)
        self.procDone.emit(True)   


class AddProgresWin(QtGui.QWidget):
    def __init__(self, parent=None):
        super(AddProgresWin, self).__init__(parent)

        self.thread = Progress()
        self.nameLine = QtGui.QLineEdit()
    
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setMinimum(1)
        self.progressbar.setMaximum(100)
        self.progressbar.setFixedWidth(400)
    
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.progressbar, 0, 0)
    
        self.setLayout(mainLayout)
        self.setWindowTitle("Solving")

        self.thread.partDone.connect(self.updatePBar)
        self.thread.procDone.connect(self.fin)
        self.thread.start()

    def updatePBar(self, val):
        self.progressbar.setValue(val)
    
    def fin(self):
        sys.exit()
        

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.path)

    pbarwin = AddProgresWin()
    pbarwin.show()

    app.exec_()
    
