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
            [sg.Text('EMCenter Positioner Control', font=('Courier',10), text_color='red')],
            [sg.Text('')],
            # Status Area
            [sg.Text('Status', font=('Courier',10), text_color='blue')],
            [sg.Text('EMCenter Status: ', font=('Courier',10), size=(25,1)), 
             sg.InputText('Getting Status...', disabled=True, font=('Courier',10), key='-Status-', size=(25,1)),
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Text('', size=(4,1)), sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetStatus')],
            [sg.Text('')],
            [sg.Text('Mast Position: ', font=('Courier',10), size=(25,1)), 
             sg.InputText('Getting Status...', disabled=True, font=('Courier',10), key='-Mast-', size=(25,1))], 
            [sg.Text('Turntable Position: ', font=('Courier',10), size=(25,1)), 
             sg.InputText('Getting Status...', disabled=True, font=('Courier',10), key='-Turntable-', size=(25,1))], 
            [sg.Text('')],
            # Settings Area
            [sg.Text('Settings', font=('Courier',10), size=(25,1), text_color='blue')],
            [sg.Text('Mast Upper Limit', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-MastUL-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetMastUL-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetMastUL-')],
            [sg.Text('Mast Lower Limit', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-MastLL-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetMastLL-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetMastLL-')],
            [sg.Text('Turntable Upper Limit', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-TableUL-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetTableUL-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetTableUL-')],
            [sg.Text('Turntable Lower Limit', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-TableLL-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetTableLL-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetTableLL-')],
            [sg.Text('Mast Speed', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-MastSpeed-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetMastSpeed-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetMastSpeed-')],
            [sg.Text('Turntable Speed', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-TableSpeed-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetTableSpeed-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetTableSpeed-')],
            [sg.Text('Mast Acceleration', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-MastAccel-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetMastAccel-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetMastAccel-')],
            [sg.Text('Turntable Acceleration', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-TableAccel-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetTableAccel-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetTableAccel-')],
            [sg.Text('Mast Cycles', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-MastCycles-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetMastCycles-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetMastCycles-')],
            [sg.Text('Turntable Cycles', font=('Courier',10), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',10), key='-TableCycles-', size=(25,1)), 
             sg.Text('',font=('Courier',10), size=(5,1)),
             sg.Button('Set', font=('Courier',10), size=(4,1), key='-SetTableCycles-'), 
             sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetTableCycles-')],
            [sg.Text('')],
            # Command Area
            [sg.Text('Scan', font=('Courier',10), size=(25,1)),
             sg.InputText('Getting Status...', disabled=True, font=('Courier',10), key='-Scanning-', size=(25,1)), 
             sg.Text('', font=('Courier',10), size=(5,1)), 
             sg.Button('Start', font=('Courier',10), size=(5,1), key='-StartScan-')], 
            [sg.Text('Manual Cmd: ', font=('Courier',10), size=(25,1)), 
             sg.InputText('', disabled=False, font=('Courier',10), key='-ManualCmd-', size=(25,1)), 
             sg.Text('', font=('Courier',10), size=(5,1)), 
             sg.Button('Send', font=('Courier',10), size=(5,1), key='-SendManualCmd-')],
            [sg.Text('')],
            [sg.Text('')],
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

        # set up function callbacks
        self.funcTbl = {
            '-SetMastUL-': lambda _x: self.setUpperLimit('A', _x),
            '-GetMastUL-': lambda _x: self.getUpperLimit('A'),
            '-SetMastLL-': lambda _x: self.setLowerLimit('A', _x),
            '-GetMastLL-': lambda _x: self.getLowerLimit('A'),
            '-SetTableUL-': lambda _x: self.setUpperLimit('B', _x),
            '-GetTableUL-': lambda _x: self.getUpperLimit('B'),
            '-SetTableLL-': lambda _x: self.setLowerLimit('B', _x),
            '-GetTableLL-': lambda _x: self.getLowerLimit('B'),
            '-SetMastSpeed-': lambda _x: self.setSpeed('A', _x),
            '-GetMastSpeed-': lambda _x: self.getSpeed('A'),
            '-SetTableSpeed-': lambda _x: self.setSpeed('B', _x),
            '-GetTableSpeed-': lambda _x: self.getSpeed('B'),
            '-SetMastAccel-': lambda _x: self.setAcceleration('A', _x),
            '-GetMastAccel-': lambda _x: self.getAcceleration('A'),
            '-SetTableAccel-': lambda _x: self.setAcceleration('B', _x),
            '-GetTableAccel-': lambda _x: self.getAcceleration('B'),
            '-SetMastCycles-': lambda _x: self.setCycles('A', _x),
            '-GetMastCycles-': lambda _x: self.getCycles('A'),
            '-SetTableCycles-': lambda _x: self.setCycles('B', _x),
            '-GetTableCycles-': lambda _x: self.getCycles('B'),
            '-SendManualCmd-': lambda _x: self.sendCmd(_x)
        }

        self.widgetTbl = {
            '-SetMastUL-': '-MastUL-',
            '-GetMastUL-': '-MastUL-',
            '-SetMastLL-': '-MastLL-',
            '-GetMastLL-': '-MastLL-',
            '-SetTableUL-': '-TableUL-',
            '-GetTableUL-': '-TableUL-',
            '-SetTableLL-': '-TableLL-',
            '-GetTableLL-': '-TableLL-',
            '-SetMastSpeed-': '-MastSpeed-',
            '-GetMastSpeed-': '-MastSpeed-',
            '-SetTableSpeed-': '-TableSpeed-',
            '-GetTableSpeed-': '-TableSpeed-',
            '-SetMastAccel-': '-MastAccel-',
            '-GetMastAccel-': '-MastAccel-',
            '-SetTableAccel-': '-TableAccel-',
            '-GetTableAccel-': '-TableAccel-',
            '-SetMastCycles-': '-MastCycles-',
            '-GetMastCycles-': '-MastCycles-',
            '-SetTableCycles-': '-TableCycles-',
            '-GetTableCycles-': '-TableCycles-',
            '-SendManualCmd-': '-ManualCmd-'
        }

        # status codes
        self.OK = True
        self.Error = False
        self.errorCode = ''

        # FIXME get from config file, CLI, or determine from device itself
        self.slot = 2

        self.openPort()
        if not self.checkStatus():
            print("Error with EMCenter, check that the device is ON and connected via USB.")
    
    def openPort(self):
        pass

    def sendCmd(self, cmd):
        print(cmd)
        return self.OK

    def createCmdStr(self, slot='', axis='', cmd='', val=''):
        # create the full string command
        cmdStr = ''
        if val == '':
            cmdStr = str(slot) + str(axis) + str(cmd)
        else:
            cmdStr = str(slot) + str(axis) + str(cmd) + ' ' + str(val)

        return cmdStr

    def checkStatus(self):
        cmd = 'STATUS?'
        cmdStr = self.createCmdStr('','',cmd)
        status = self.sendCmd(cmdStr)
        return status

    def startScan(self, iterations, axis):
        cmd = 'SC'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
        return status

    def isScanning(self, axis):
        cmd = 'SC?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
        return status

    def stop(self, axis):
        cmd = 'ST'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
        pass

    def getCurrentPosition(self, axis):
        cmd = 'CP?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
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

        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=pos)
        status = self.sendCmd(cmdStr)

        return status

    def setUpperLimit(self, axis, limit):
        cmd = 'CL'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=limit)
        status = self.sendCmd(cmdStr)
        pass

    def getUpperLimit(self, axis):
        cmd = 'CL?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
        pass

    def setLowerLimit(self, axis, limit):
        cmd = 'WL'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=limit)
        status = self.sendCmd(cmdStr)
        pass

    def getLowerLimit(self, axis):
        cmd = 'WL?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
        pass

    def setSpeed(self, axis, speed):
        cmd = 'SPEED'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=speed)
        status = self.sendCmd(cmdStr)
        pass

    def getSpeed(self, axis):
        cmd = 'SPEED?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
        pass

    def setAcceleration(self, axis, accel):
        cmd = 'ACC'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=accel)
        status = self.sendCmd(cmdStr)
        pass

    def getAcceleration(self, axis):
        cmd = 'ACC?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
        pass

    def setCycles(self, axis, cycles):
        cmd = 'CY'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=cycles)
        status = self.sendCmd(cmdStr)
        pass

    def getCycles(self, axis):
        cmd = 'CY?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
        pass

    def getType(self):
        cmd = 'TYP?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        status = self.sendCmd(cmdStr)
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
                # call function from dictionary
                if self.funcTbl.get(event) != None:
                    if self.widgetTbl.get(event) != None:
                        val = values[self.widgetTbl.get(event)]
                        self.funcTbl.get(event)(val)
                else:
                    print(event)

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

    for opt, arg in opts:
        if opt == '-h':
            usage()
            return

    ctrl = EMCenterController('COM6')
    ctrl.run()

# callable from command line
if __name__ == "__main__":
    main(sys.argv[1:])