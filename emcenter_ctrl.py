#!/usr/bin/env python3

import matplotlib
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation
from matplotlib import style

import sys
import os
import getopt
import logging

import serial
import io

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

        self.widgetMap = {
            '-GetStatus-': '-Status-',
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
            '-StartMastScan-': '-MastScanning-',
            '-StartTableScan-': '-TableScanning-',
            '-SendManualCmd-': '-ManualCmd-'
        }

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
             sg.Text('', size=(4,1)), sg.Button('Get', font=('Courier',10), size=(4,1), key='-GetStatus-')],
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
             sg.InputText('Getting Status...', disabled=True, font=('Courier',10), key='-MastScanning-', size=(25,1)), 
             sg.Text('', font=('Courier',10), size=(5,1)), 
             sg.Button('Start', font=('Courier',10), size=(5,1), key='-StartMastScan-')], 
            [sg.Text('Scan', font=('Courier',10), size=(25,1)),
             sg.InputText('Getting Status...', disabled=True, font=('Courier',10), key='-TableScanning-', size=(25,1)), 
             sg.Text('', font=('Courier',10), size=(5,1)), 
             sg.Button('Start', font=('Courier',10), size=(5,1), key='-StartTableScan-')], 
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
        
        # status codes
        self.OK = True
        self.Error = False
        self.errorCode = ''
        
        # FIXME get from config file, CLI, or determine from device itself
        self.slot = 2

        # open serial port
        self.port = port
        self._serial = None
        self.serialIO = None
        if not self.openPort():
            print("Error opening seral port, exiting...")
            exit(-1)

        if not self.getStatus():
            print("Error with EMCenter, check that the device is ON and connected via USB.")
            exit(-1)

        # defaults
        self.status = self.OK
        self.mastLL = 0
        self.mastUL = 0
        self.tableLL = 0
        self.tableUL = 0
        self.mastSpeed = 0
        self.tableSpeed = 0
        self.mastAccel = 0
        self.tableAccel = 0
        self.mastCycles = 0
        self.tableCycles = 0
        self.mastScanning = False
        self.tableScanning = False
        self.mastPosition = 0
        self.tablePosition = 0
        self.mastZeroDegOffset = 0
        self.tableZeroDegOffset = 0

        # Create UI
        self.gui = EMCenerCtrlGUI()

        # set up function callbacks
        self.funcTbl = {
            '-GetStatus-': lambda _x: self.getStatus(),
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
            '-StartMastScan-': lambda _x: self.startScan('A'),
            '-StartTableScan-': lambda _x: self.startScan('B'),
            '-SendManualCmd-': lambda _x: self.sendCmd(_x)
        }

    def openPort(self):
        ret = self.OK
        try:
            self._serial = serial.Serial(self.port, 115200, timeout=5, 
                parity=serial.PARITY_NONE, write_timeout=5)
            self.serialIO = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
            ret = self.OK
        except serial.SerialException as e:
            print("Serial port exception: " + e.strerror)    
            ret = self.Error
            
        return ret 

    def writePort(self, val):
        ret = 0 
        try:
            if self.serialIO != None:
                ret = self.serialIO.write(str(val) + '\n')
                self.serialIO.flush()
        except serial.SerialTimeoutException as e:
            print("Timeout in serial port write: " + e.strerror)
        except serial.SerialException as e:
            print("Exception in serial port write: " + e.strerror)


        return ret

    def readPort(self):
        ret = None
        try:
            if self.serialIO != None:
                ret = self.serialIO.readline()
        except serial.SerialTimeoutException as e:
            print("Timeout in serial port read: " + e.strerror)
        except serial.SerialException as e:
            print("Exception in serial port read: " + e.strerror)

        return ret

    def sendCmd(self, cmd):
        print(cmd)
        resp = None

        n = self.writePort(cmd)
        if n > 0:
            resp = self.readPort()
        else:
            print("Error: Wrote " + str(n) + " bytes!")

        return resp

    def createCmdStr(self, slot='', axis='', cmd='', val=''):
        # create the full string command
        cmdStr = ''
        if val == '':
            cmdStr = str(slot) + str(axis) + str(cmd)
        else:
            cmdStr = str(slot) + str(axis) + str(cmd) + ' ' + str(val)

        return cmdStr

    # set and get functions for all configurable items.  All function return OK
    # or Error depending on the response received.  Error is only return if no 
    # response is received.
    def get(self, cmdStr):
        resp = self.sendCmd(cmdStr)
        
        if resp == None:
            print("Error in get command: " + cmdStr)
            status = self.Error
        else:
            self.status = resp 

        return status, resp
    
    def set(self, cmdStr):
        resp = self.sendCmd(cmdStr)
        
        if resp == None:
            print("Error in set command: " + cmdStr)
            status = self.Error
        else:
            self.status = resp 

        return status

    def getStatus(self):
        cmd = 'STATUS?'
        cmdStr = self.createCmdStr('','',cmd)

        resp = self.get(cmdStr)
        if resp[0] != None:
            self.status = resp[1]

    def startScan(self, axis):
        cmd = 'SC'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
        return status

    def isScanning(self, axis):
        cmd = 'SC?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
        return status

    def stop(self, axis):
        cmd = 'ST'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
        pass

    def getCurrentPosition(self, axis):
        cmd = 'CP?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
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
        resp = self.sendCmd(cmdStr)

        return status

    def setUpperLimit(self, axis, limit):
        cmd = 'CL'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=limit)
        resp = self.sendCmd(cmdStr)
        pass

    def getUpperLimit(self, axis):
        cmd = 'CL?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
        pass

    def setLowerLimit(self, axis, limit):
        cmd = 'WL'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=limit)
        resp = self.sendCmd(cmdStr)
        pass

    def getLowerLimit(self, axis):
        cmd = 'WL?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
        pass

    def setSpeed(self, axis, speed):
        cmd = 'SPEED'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=speed)
        resp = self.sendCmd(cmdStr)
        pass

    def getSpeed(self, axis):
        cmd = 'SPEED?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
        pass

    def setAcceleration(self, axis, accel):
        cmd = 'ACC'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=accel)
        resp = self.sendCmd(cmdStr)
        pass

    def getAcceleration(self, axis):
        cmd = 'ACC?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
        pass

    def setCycles(self, axis, cycles):
        cmd = 'CY'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=cycles)
        resp = self.sendCmd(cmdStr)
        pass

    def getCycles(self, axis):
        cmd = 'CY?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
        pass

    def getType(self):
        cmd = 'TYP?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.sendCmd(cmdStr)
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
                    if self.gui.widgetMap.get(event) != None:
                        val = values[self.gui.widgetMap.get(event)]
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