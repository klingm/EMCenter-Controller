#!/usr/bin/env python3

import matplotlib
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation
from matplotlib import style

import sys
import os
import time
import math
import statistics
import getopt
import logging
import subprocess
import threading
import readline

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import (NavigationToolbar2Tk as NavigationToolbar)

from datetime import datetime
import time

matplotlib.use('TkAgg')

class EMCenerCtrlGUI:
    def __init__(self):
        super().__init__()

        # set the theme for the window
        sg.theme('Reddit')

        # TO DO, add plots showing Az/El antenna position

        # col 1
        col1 = [
            [sg.Text('EMCenter Positioner Control', font=('Courier',12))],
            [sg.OK()]
        ]

        layout = [[sg.Column(col1)]]
        window = sg.Window('EMCenter Positioner Control', layout, resizable=False, finalize=True)
        self.window = window
        
class EMCenterController:
    def __init__(self, port):
        super().__init__()
        self.gui = EMCenerCtrlGUI()
        self.port = port

        # status codes
        self.OK = True
        self.Error = False
        self.errorCode = ''

        self.openPort()
        if not self.checkStatus():
            print("Error with EMCenter, check that the device is ON and connected via USB.")
    
    def openPort(self):
        pass

    def sendCmd(self, cmd):
        return self.OK

    def checkStatus(self):
        pass

    def startScan(self, iterations, axis):
        cmd = 'SC'
        pass

    def isScanning(self, axis):
        cmd = 'SC?'
        pass

    def stop(self, axis):
        cmd = 'ST'
        pass

    def getCurrentPosition(self, axis):
        cmd = 'CP?'
        pos = 0

        return pos

    def seekPosition(self, axis, pos):
        status = 0
        cp = self.getCurrentPosition(axis)
        if cp < pos:
            cmd = 'SKP'
        elif cp > pos:
            cmd = 'SKN'
        else:
            return self.OK

        status = self.sendCmd(cmd)

        return status

    def setUpperLimit(self, axis, limit):
        pass

    def getUpperLimit(self, axis):
        pass

    def setLowerLimit(self, axis, limit):
        pass

    def getLowerLimit(self, axis):
        pass

    def setSpeed(self, axis, speed):
        pass

    def getSpeed(self, axis):
        pass

    def setAcceleration(self, axis, accel):
        pass

    def getAcceleration(self, axis, accel):
        pass

    def run(self):
        done = False
        while(not done):
            # wait for user action, or timeout.  On timeout update the window.
            event, values = self.gui.window.read(timeout=500, timeout_key='-Timeout-')

            if event in (None, 'Exit'):
                print('Exiting window')
                done = True
            elif event in (None, 'OK'):
                print('OK')
            elif event in (None, '-Timeout-'):
                pass
            else:
                print('Unknown command')

    # print usage info
def usage():
    print("\nDescription: Controller for the ETS-Lindgren EMCenter 2-axis Antenna Positioner\n")
    print("\nUsage:\n")
    print(" ",__file__, " [-h]\n")
    print("     -h: help\n")
    print("\n")

# main function for command line entry point
def main(argv):
    # grab command line args
    try:
        opts, args = getopt.getopt(argv,"h")
    except getopt.GetoptError:
        usage()
        return

    verbose = False
    for opt, arg in opts:
        if opt == '-h':
            usage()
            return

    ctrl = EMCenterController('COM6')
    ctrl.run()

# callable from command line
if __name__ == "__main__":
    main(sys.argv[1:])