#!/usr/bin/env python3

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation
from matplotlib import style

import sys
import os
import getopt
import logging
import threading

import serial
import io

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import (NavigationToolbar2Tk as NavigationToolbar)

from datetime import datetime
import time

import socket

# This class uses the PySimpleGUI module to create a simple UI with widgets to
# allow user control of a ETS-Lindgren 2-axis antenna positioner using EMCenter.
# When an instance is created the window is opened.  Function callbacks for 
# each interactive widget are handled by the creator.
class EMCenerCtrlGUI:
    def __init__(self):
        super().__init__()

        # set the theme for the window
        sg.theme('Reddit')

        self.widgetMap = {
            '-SetMastUL-': '-NewMastUL-',
            '-GetMastUL-': '-CurrMastUL-',
            '-SetMastLL-': '-NewMastLL-',
            '-GetMastLL-': '-CurrMastLL-',
            '-SetTableUL-': '-NewTableUL-',
            '-GetTableUL-': '-CurrTableUL-',
            '-SetTableLL-': '-NewTableLL-',
            '-GetTableLL-': '-CurrTableLL-',
            '-SetMastSpeed-': '-NewMastSpeed-',
            '-GetMastSpeed-': '-CurrMastSpeed-',
            '-SetTableSpeed-': '-NewTableSpeed-',
            '-GetTableSpeed-': '-CurrTableSpeed-',
            '-SetMastAccel-': '-NewMastAccel-',
            '-GetMastAccel-': '-CurrMastAccel-',
            '-SetTableAccel-': '-NewTableAccel-',
            '-GetTableAccel-': '-CurrTableAccel-',
            '-SetMastCycles-': '-NewMastCycles-',
            '-GetMastCycles-': '-CurrMastCycles-',
            '-SetTableCycles-': '-NewTableCycles-',
            '-GetTableCycles-': '-CurrTableCycles-',
            '-StartMastScan-': '-MastScanning-',
            '-StartTableScan-': '-TableScanning-',
            '-StartMastSeek-': '-MastSeekPos-',
            '-StartTableSeek-': '-TableSeekPos-',
            '-StopMast-': '',
            '-StopTable-': '',
            '-SendManualCmd-': '-ManualCmd-'
        }

        # TO DO, add plots showing Az/El antenna position

        # col 1
        col1 = [
            [sg.Text('EMCenter Positioner Control', font=('Courier',8), text_color='red')],
            # Status Area
            [sg.Text('Status', font=('Courier',8), text_color='blue')],
            [sg.Text('EMCenter Status: ', font=('Courier',8), size=(25,1)), 
             sg.InputText('Getting Status...', disabled=True, font=('Courier',8), key='-Status-', size=(25,1)),
             sg.Text('',font=('Courier',8), size=(5,1))],
            [sg.Text('')],
            [sg.Text('Mast Position: ', font=('Courier',8), size=(25,1)), 
             sg.InputText('Getting Status...', disabled=True, font=('Courier',8), key='-MastPosition-', size=(25,1))], 
            [sg.Text('Turntable Position: ', font=('Courier',8), size=(25,1)), 
             sg.InputText('Getting Status...', disabled=True, font=('Courier',8), key='-TablePosition-', size=(25,1))], 
            [sg.Text('')],
            # Settings Area
            [sg.Text('Settings', font=('Courier',8), size=(25,1), text_color='blue')],
            [sg.Text('Mast Upper Limit', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewMastUL-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrMastUL-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetMastUL-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetMastUL-')],
            [sg.Text('Mast Lower Limit', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewMastLL-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrMastLL-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetMastLL-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetMastLL-')],
            [sg.Text('Turntable Upper Limit', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewTableUL-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrTableUL-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetTableUL-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetTableUL-')],
            [sg.Text('Turntable Lower Limit', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewTableLL-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrTableLL-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetTableLL-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetTableLL-')],
            [sg.Text('Mast Speed', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewMastSpeed-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrMastSpeed-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetMastSpeed-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetMastSpeed-')],
            [sg.Text('Turntable Speed', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewTableSpeed-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrTableSpeed-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetTableSpeed-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetTableSpeed-')],
            [sg.Text('Mast Acceleration', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewMastAccel-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrMastAccel-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetMastAccel-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetMastAccel-')],
            [sg.Text('Turntable Acceleration', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewTableAccel-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrTableAccel-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetTableAccel-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetTableAccel-')],
            [sg.Text('Mast Cycles', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewMastCycles-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrMastCycles-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetMastCycles-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetMastCycles-')],
            [sg.Text('Turntable Cycles', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-NewTableCycles-', size=(12,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-CurrTableCycles-', size=(12,1)), 
             sg.Text('',font=('Courier',8), size=(4,1)),
             sg.Button('Set', font=('Courier',8), size=(4,1), key='-SetTableCycles-'), 
             sg.Button('Get', font=('Courier',8), size=(4,1), key='-GetTableCycles-')],
            [sg.Text('')],
            # Command Area
            [sg.Text('Commands', font=('Courier',8), size=(25,1), text_color='blue')],
            [sg.Text('Mast Scan Mode', font=('Courier',8), size=(25,1)),
             sg.InputText('Getting Status...', disabled=True, font=('Courier',8), key='-MastScanning-', size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(5,1)), 
             sg.Button('Start', font=('Courier',8), size=(5,1), key='-StartMastScan-')], 
            [sg.Text('Table Scan Mode', font=('Courier',8), size=(25,1)),
             sg.InputText('Getting Status...', disabled=True, font=('Courier',8), key='-TableScanning-', size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(5,1)), 
             sg.Button('Start', font=('Courier',8), size=(5,1), key='-StartTableScan-')], 
            [sg.Text('Mast Seek Pos', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-MastSeekPos-', size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(5,1)), 
             sg.Button('Start', font=('Courier',8), size=(5,1), key='-StartMastSeek-')], 
            [sg.Text('Table Seek Pos', font=('Courier',8), size=(25,1)),
             sg.InputText('', disabled=False, font=('Courier',8), key='-TableSeekPos-', size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(5,1)), 
             sg.Button('Start', font=('Courier',8), size=(5,1), key='-StartTableSeek-')], 
            [sg.Text('Stop Mast: ', font=('Courier',8), size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(5,1)), 
             sg.Button('Stop', font=('Courier',8), size=(5,1), key='-StopMast-')],
            [sg.Text('Stop Table: ', font=('Courier',8), size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(5,1)), 
             sg.Button('Stop', font=('Courier',8), size=(5,1), key='-StopTable-')],
            [sg.Text('Manual Cmd: ', font=('Courier',8), size=(25,1)), 
             sg.InputText('', disabled=False, font=('Courier',8), key='-ManualCmd-', size=(25,1)), 
             sg.Text('', font=('Courier',8), size=(5,1)), 
             sg.Button('Send', font=('Courier',8), size=(5,1), key='-SendManualCmd-')],
            [sg.Text('Cmd Resp: ', font=('Courier',8), size=(25,1)), 
             sg.InputText('', disabled=True, font=('Courier',8), key='-ManualCmdResp-', size=(25,1))], 
        ]

        layout = [[sg.Column(col1)]]

        window = sg.Window('EMCenter Positioner Control', layout, resizable=False, finalize=True)
        self.window = window

# This class uses the published serial port API for the ETS-Lindgren EMCenter
# controller to send commands and retrieve status of a 2-axis antenna 
# positioner.  Commands are send and received via TCP/IP to a tcp to serial
# "pipe" running on a computer connected via USB to the EMCenter.  The remote 
# address and port for the TCP/IP connection must be specified.  Running in 
# local mode is also supported by specifying the serial COM port that the 
# EMCenter is connected to.
class EMCenterController:
    def __init__(self, port='', remoteAddr='', remotePort=''):
        super().__init__()
        self.debug = False

        # check for remote socket mode
        self.mode = 'local'
        self.remoteAddr = remoteAddr
        self.remotePort = remotePort
        if self.remoteAddr != '':
            self.mode = 'socket'
        
        # check for valid input args for 'socket' mode
        if self.mode == 'socket' and self.remotePort == '':
            print('Error, must specify a remote port for socket connection!')
            exit(-1)
        elif self.mode == 'socket' and self.remotePort != '':
            self.remotePort = int(self.remotePort)
        
        # Objects for async GUI updates.  Status widgets are updated 
        # periodically using a dedicated thread so accessing their contents 
        # must be protected using Mutex's as string datatype operations cannot
        # be guaranteed to be atomic.
        self.refreshMutex = threading.Lock()
        self.cmdMutex = threading.Lock()
        self.refreshThread = None
        self.doneFlag = False

        # status codes
        self.OK = True
        self.Error = False
        self.errorCode = ''
        
        # FIXME get from config file, CLI, or determine from device itself
        self.slot = 2
        self.mastAxis = 'A'
        self.tableAxis = 'B'

        # open serial port
        self.port = port
        self._port = None
        self.serialIO = None
        if not self.openPort():
            if self.mode == 'socket':
                print("Error opening socket, exiting...")
            else:
                print("Error opening serial port, exiting...")
            exit(-1)

        # defaults
        self.status = self.OK
        self.mastLL = "Unknown..."
        self.mastUL = "Unknown..."
        self.tableLL = "Unknown..."
        self.tableUL = "Unknown..."
        self.mastSpeed = "Unknown..."
        self.tableSpeed = "Unknown..."
        self.mastAccel = "Unknown..."
        self.tableAccel = "Unknown..."
        self.mastCycles = "Unknown..."
        self.tableCycles = "Unknown..."
        self.mastScanning = "Unknown..."
        self.tableScanning ="Unknown..."
        self.mastSeekPos = ''
        self.tableSeekPos = ''
        self.mastPosition = "Unknown..."
        self.tablePosition = "Unknown..."
        self.mastZeroDegOffset = "Unknown..."
        self.tableZeroDegOffset = "Unknown..."

        # Create UI
        #self.gui = EMCenerCtrlGUI()

        # set up function callbacks
        self.funcTbl = {
            '-SetMastUL-': lambda _x: self.setUpperLimit(self.mastAxis, _x),
            '-GetMastUL-': lambda _x: self.getUpperLimit(self.mastAxis),
            '-SetMastLL-': lambda _x: self.setLowerLimit(self.mastAxis, _x),
            '-GetMastLL-': lambda _x: self.getLowerLimit(self.mastAxis),
            '-SetTableUL-': lambda _x: self.setUpperLimit(self.tableAxis, _x),
            '-GetTableUL-': lambda _x: self.getUpperLimit(self.tableAxis),
            '-SetTableLL-': lambda _x: self.setLowerLimit(self.tableAxis, _x),
            '-GetTableLL-': lambda _x: self.getLowerLimit(self.tableAxis),
            '-SetMastSpeed-': lambda _x: self.setSpeed(self.mastAxis, _x),
            '-GetMastSpeed-': lambda _x: self.getSpeed(self.mastAxis),
            '-SetTableSpeed-': lambda _x: self.setSpeed(self.tableAxis, _x),
            '-GetTableSpeed-': lambda _x: self.getSpeed(self.tableAxis),
            '-SetMastAccel-': lambda _x: self.setAccSHUT_RDWReleration(self.mastAxis, _x),
            '-GetMastAccel-': lambda _x: self.getAcceleration(self.mastAxis),
            '-SetTableAccel-': lambda _x: self.setAcceleration(self.tableAxis, _x),
            '-GetTableAccel-': lambda _x: self.getAcceleration(self.tableAxis),
            '-SetMastCycles-': lambda _x: self.setCycles(self.mastAxis, _x),
            '-GetMastCycles-': lambda _x: self.getCycles(self.mastAxis),
            '-SetTableCycles-': lambda _x: self.setCycles(self.tableAxis, _x),
            '-GetTableCycles-': lambda _x: self.getCycles(self.tableAxis),
            '-StartMastScan-': lambda _x: self.startScan(self.mastAxis),
            '-StartTableScan-': lambda _x: self.startScan(self.tableAxis),
            '-StartMastSeek-': lambda _x: self.seekPosition(self.mastAxis, _x),
            '-StartTableSeek-': lambda _x: self.seekPosition(self.tableAxis, _x),
            '-StopMast-': lambda _x: self.stop(self.mastAxis),
            '-StopTable-': lambda _x: self.stop(self.tableAxis),
            '-SendManualCmd-': lambda _x: self.sendCmd(_x)
        }
        
        # get default values on init, these will be populated in the GUI on the 
        # first iteration of run loop.
        self.getCurrentPosition(self.mastAxis)
        self.getCurrentPosition(self.tableAxis)
        self.getUpperLimit(self.mastAxis)
        self.getUpperLimit(self.tableAxis)
        self.getLowerLimit(self.mastAxis)
        self.getLowerLimit(self.tableAxis)
        self.getSpeed(self.mastAxis)
        self.getSpeed(self.tableAxis)
        self.getAcceleration(self.mastAxis)
        self.getAcceleration(self.tableAxis)
        self.getCycles(self.mastAxis)
        self.getCycles(self.tableAxis)

    # implicit destructor, call the kill() function for the object to 
    # gracefully close all opened devices, etc.
    def __del__(self):
        #print('EMCenterController dtor')
        self.kill()
    
    # Gracefully close socket, serial port, and IO handles
    def kill(self):
        if self._port != None:
            try:
                self.serialIO.close()
                self._port.close()
                if self.mode == 'socket':
                    self._sock.shutdown(socket.SHUT_RDWR)
                    self._sock.close()
                    self._sock = None
            except serial.SerialException as e:
                if e.strerror != None:
                    print('Except in closing serial port: ' + e.strerror)
            except socket.error as e:
                if e.strerror != None:
                    print('Except in closing socket: ' + e.strerror)


            self.serialIO = None 
            self._port = None

    # Open the serial port or socket depending on the specified mode.  When in 
    # socket mode, the socket.makefile() function is used to create a 
    # readable/writeable binary "file" that can be used with the IO 
    # BufferedRWPair object.  When in serial port mode, the serial port object
    # can directly be used with BufferRWPair.
    def openPort(self):
        ret = self.OK
        try:
            if self.mode == 'socket':
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, )
                self._sock.connect((self.remoteAddr, self.remotePort))
                self._port = self._sock.makefile('rwb', buffering=0)
            else:
                self._port = serial.Serial(self.port, 115200, timeout = 0.1,
                    parity=serial.PARITY_NONE)
            
            self.serialIO = io.TextIOWrapper(io.BufferedRWPair(self._port, self._port))
            ret = self.OK
        except serial.SerialException as e:
            if e.strerror != None:
                print("Serial port exception: " + e.strerror)    
            ret = self.Error
        except socket.error as e:
            if e.strerror != None:
                print("Socket exception: " + e.strerror)    
            ret = self.Error
            
        return ret 


    # Low level write function that uses the BufferedRWPair object to write 
    # data to the port, this works the same for socket or serial port mode.
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

    # Low level read function that uses the BufferedRWPair object to read 
    # data from the port, this works the same for socket or serial port mode. 
    # Note that the readline function is used and then the trailing newline 
    # char is stripped.
    def readPort(self):
        ret = None
        try:
            if self.serialIO != None:
                ret = self.serialIO.readline()
        except serial.SerialTimeoutException as e:
            print("Timeout in serial port read: " + e.strerror)
        except serial.SerialException as e:
            print("Exception in serial port read: " + e.strerror)

        return str(ret).rstrip()

    # Low level function to send a command using the class writePort() function
    # to send and then uses the class readPort() function to read the command 
    # status/response.
    def sendCmd(self, cmd):
        if cmd == '':
            return 'Enter a command' 

        if self.debug:
            print('DEBUG: ' + cmd)

        resp = None

        n = self.writePort(cmd)
        if n > 0:
            resp = self.readPort()
        else:
            print("Error: Wrote " + str(n) + " bytes!")

        return resp

    # Create a command string based on the given arguments.  Command strings 
    # are always in the following format:
    #
    #   [Slot][Axis][Cmd] [Val]
    #
    # Where:
    #   - Slot is the EMCenter slot number of the positioner controller card
    #   - Axis is the device ID for the specified axis, either 'A' or 'B'
    #   - Cmd is the cmd string specified in the EMCenter EMControl manual.
    #   - Val is the value specified for the associated cmd string in the 
    #     EMControl manual
    #
    #   Example: 2ASKP 0
    #       Command the mast to seek to position 0 degrees.
    #
    def createCmdStr(self, slot='', axis='', cmd='', val=''):
        # create the full string command
        cmdStr = ''
        if val == '':
            cmdStr = str(slot) + str(axis) + str(cmd)
        else:
            cmdStr = str(slot) + str(axis) + str(cmd) + ' ' + str(val)

        return cmdStr

    # get function for all configurable items.  All function return OK or Error 
    # depending on the response received; the response itself is returned as 
    # well.  Error is only return if no response is received.
    def get(self, cmdStr):
        resp = None
        status = None
        with self.cmdMutex:
            resp = self.sendCmd(cmdStr)
            
            status = self.OK
            if resp == None:
                print("get ERROR (cmd): " + cmdStr)
                print("get ERROR (resp): " + resp)
                status = self.Error
            else:
                if self.debug:
                    print('DEBUG: ' + resp)

        return status, resp
    
    # set function for all configurable items.  All function return OK or Error 
    # depending on the response received; the response itself is returned as 
    # well.  Error is only return if no response is received.
    def set(self, cmdStr):
        resp = None
        status = None
        with self.cmdMutex:
            resp = self.sendCmd(cmdStr)
            
            status = self.OK
            if resp == None:
                print("Error in set command: " + cmdStr)
                status = self.Error
            elif resp != 'OK':
                status = self.Error
                print('set ERROR (cmd): ' + cmdStr)
                print('set ERROR (resp): ' + resp)
            else:
                if self.debug:
                    print('DEBUG: ' + resp)

        return status, resp

    # Function to get the current EMCenter status, return is a tuple containing
    # command exeuction status and command response.
    def getStatus(self, update=True):
        cmd = 'STATUS?'
        cmdStr = self.createCmdStr('','',cmd)

        resp = self.get(cmdStr)
        if resp[0] != None and update:
            self.status = resp[1]

        return resp

    # Function to start a scan on the specified axis, return is a tuple containing
    # command exeuction status and command response.
    def startScan(self, axis):
        cmd = 'SC'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.set(cmdStr)

        return resp

    # Function to query scan status on the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def isScanning(self, axis, update=True):
        cmd = 'SC?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.get(cmdStr)
        if resp[0] != None and update:
            if axis == self.mastAxis:
                self.mastScanning = resp[1]
            else:
                self.tableScanning = resp[1]

        return resp

    # Function to stop motion of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def stop(self, axis):
        cmd = 'ST'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        resp = self.set(cmdStr)

        return resp

    # Function to query the current position of the specified axis, return is a
    # tuple containing command exeuction status and command response.
    def getCurrentPosition(self, axis, update=True):
        cmd = 'CP?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)
        
        resp = self.get(cmdStr)
        if resp[0] != None and update:
            if axis == self.mastAxis:
                self.mastPosition = resp[1]
            else:
                self.tablePosition = resp[1]

        return resp

    # Function to seek the specified position on the specified axis, return is a
    # tuple containing command exeuction status and command response. Logic to 
    # determine whether to issue a seek positive (CW) or seek negative (CCW)
    # command is implemented by using the current position cached in a class 
    # member variable.
    def seekPosition(self, axis, pos):
        cp = 0
        cmd = ''
        resp = None

        if axis == self.mastAxis and self.mastScanning == '1':
            print('Error: stop scanning before issuing seek cmd!')
            return self.Error
        elif axis == self.tableAxis and self.tableScanning == '1':
            print('Error: stop scanning before issuing seek cmd!')
            return self.Error

        try:
            if axis == self.mastAxis:
                strCp = self.mastPosition.split(' ')
                cp = float(strCp[0])
            else:
                strCp = self.tablePosition.split(' ')
                cp = float(strCp[0])
            
            if cp < float(pos):
                cmd = 'SKP'
            elif cp > float(pos):
                cmd = 'SKN'
            else:
                return self.OK

            cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=pos)
            resp = self.set(cmdStr)
        except TypeError as e:
            print("TypeError: " + e.strerror)    
            resp = self.Error, ''

        return resp

    # Function to set the upper limit of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def setUpperLimit(self, axis, limit):
        cmd = 'WL'
        if limit == '':
            limit = ' '
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=limit)
        resp1 = self.set(cmdStr)
        resp2 = self.getUpperLimit(axis)

        return resp1

    # Function to get the upper limit of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def getUpperLimit(self, axis):
        cmd = 'WL?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)

        resp = self.get(cmdStr)
        
        with self.refreshMutex:
            if resp[0] != None:
                if axis == self.mastAxis:
                    self.mastUL = resp[1]
                else:
                    self.tableUL = resp[1]

        return resp

    # Function to set the lower limit of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def setLowerLimit(self, axis, limit):
        cmd = 'CL'
        if limit == '':
            limit = ' '
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=limit)
        resp1 = self.set(cmdStr)
        resp2 = self.getUpperLimit(axis)

        return resp1

    # Function to get the lower limit of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def getLowerLimit(self, axis):
        cmd = 'CL?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)

        resp = self.get(cmdStr)
        
        with self.refreshMutex:
            if resp[0] != None:
                if axis == self.mastAxis:
                    self.mastLL = resp[1]
                else:
                    self.tableLL = resp[1]

        return resp

    # Function to set the speed of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def setSpeed(self, axis, speed):
        cmd = 'SPEED'
        if speed == '':
            speed = ' '
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=speed)
        resp1 = self.set(cmdStr)
        resp2 = self.getSpeed(axis)

        return resp1

    # Function to get the speed of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def getSpeed(self, axis):
        cmd = 'SPEED?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)

        resp = self.get(cmdStr)
        
        with self.refreshMutex:
            if resp[0] != None:
                if axis == self.mastAxis:
                    self.mastSpeed = resp[1]
                else:
                    self.tableSpeed = resp[1]

        return resp

    # Function to set the acceleration of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def setAcceleration(self, axis, accel):
        cmd = 'ACC'
        if accel == '':
            accel = ' '
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=accel)
        resp1 = self.set(cmdStr)
        resp2 = self.getAcceleration(axis)

        return resp1

    # Function to get the acceleration of the specified axis, return is a tuple 
    # containing command exeuction status and command response.
    def getAcceleration(self, axis):
        cmd = 'ACC?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)

        resp = self.get(cmdStr)
        
        with self.refreshMutex:
            if resp[0] != None:
                if axis == self.mastAxis:
                    self.mastAccel = resp[1]
                else:
                    self.tableAccel = resp[1]

        return resp

    # Function to set the scan cycle count of the specified axis, return is a 
    # tuple containing command exeuction status and command response.
    def setCycles(self, axis, cycles):
        cmd = 'CY'
        if cycles == '':
            cycles = ' '
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd,val=cycles)
        resp1 = self.set(cmdStr)
        resp2 = self.getCycles(axis)

        return resp1

    # Function to get the scan cycle count of the specified axis, return is a 
    # tuple containing command exeuction status and command response.
    def getCycles(self, axis):
        cmd = 'CY?'
        cmdStr = self.createCmdStr(slot=self.slot,axis=axis,cmd=cmd)

        resp = self.get(cmdStr)
        
        with self.refreshMutex:
            if resp[0] != None:
                if axis == self.mastAxis:
                    self.mastCycles = resp[1]
                else:
                    self.tableCycles = resp[1]

        return resp

    # Thread loop used to asynchronously update/refresh the status, current
    # position and scan state of the positioner.  The refreshMutex object is
    # used to ensure mutual exclusion from two threads accessing the string 
    # member variables simultaneously, which could result in a race condition.
    def refresh(self):
        while not self.doneFlag:
            status = self.getStatus(update=False)
            mastCp = self.getCurrentPosition(self.mastAxis, update=False)
            tableCp = self.getCurrentPosition(self.tableAxis, update=False)
            mastScan = self.isScanning(self.mastAxis, update=False)
            tableScan = self.isScanning(self.tableAxis, update=False)
        
            with self.refreshMutex:
                if status[0] != None:
                    self.status = status[1]
                if mastCp[0] != None:
                    self.mastPosition = mastCp[1]
                if tableCp[0] != None:
                    self.tablePosition = tableCp[1]
                if mastScan[0] != None:
                    self.mastScanning = mastScan[1]
                if tableScan[0] != None:
                    self.tableScanning = tableScan[1]
            
            time.sleep(1)

    # Main thread loop that creates the GUI, and then waits for user actions 
    # and updates widget field values.
    def run(self):
        # Create UI
        self.gui = EMCenerCtrlGUI()

        #spawn the refresh thread
        self.refreshThread = threading.Thread(target=self.refresh)
        self.refreshThread.start()

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
                with self.refreshMutex:
                    self.gui.window['-Status-'].Update(value=self.status)
                    self.gui.window['-MastPosition-'].Update(value=self.mastPosition)
                    self.gui.window['-TablePosition-'].Update(value=self.tablePosition)
                    self.gui.window['-CurrMastUL-'].Update(value=self.mastUL)
                    self.gui.window['-CurrMastLL-'].Update(value=self.mastLL)
                    self.gui.window['-CurrTableUL-'].Update(value=self.tableUL)
                    self.gui.window['-CurrTableLL-'].Update(value=self.tableLL)
                    self.gui.window['-CurrMastSpeed-'].Update(value=self.mastSpeed)
                    self.gui.window['-CurrTableSpeed-'].Update(value=self.tableSpeed)
                    self.gui.window['-CurrMastAccel-'].Update(value=self.mastAccel)
                    self.gui.window['-CurrTableAccel-'].Update(value=self.tableAccel)
                    self.gui.window['-CurrMastCycles-'].Update(value=self.mastCycles)
                    self.gui.window['-CurrTableCycles-'].Update(value=self.tableCycles)
                    self.gui.window['-MastScanning-'].Update(value=self.mastScanning)
                    self.gui.window['-TableScanning-'].Update(value=self.tableScanning)

            else:
                # This else block handles all user actions using a lambda 
                # lookup table from the widget 'key'.  This allows a generic 
                # loop to handle invoking all functions for user actions.  The
                # 'key' is contained in the event variable.  The value for the 
                # specified action is retrieved via lookup as well and then 
                # passed to the lambda.

                # call function from dictionary
                resp = None
                if self.funcTbl.get(event) != None:
                    if self.gui.widgetMap.get(event) != None:
                        val = None
                        if self.gui.widgetMap.get(event) != '':
                            val = values[self.gui.widgetMap.get(event)]
                        resp = self.funcTbl.get(event)(val)
                    
                    if event == '-SendManualCmd-':
                        self.gui.window['-ManualCmdResp-'].Update(value=resp)
                    elif resp[0] == self.Error:
                        sg.Popup(resp[1] +  ': ' + self.getEMCenterError(resp[1]))

                else:
                    print(event)
        
        self.doneFlag = True 

    # Lookup table for EMCenter error codes
    def getEMCenterError(self, errorCode):
        #ERROR 1 Wrong command
        #ERROR 2 Requested position too high
        #ERROR 3 Requested position too low
        #ERROR 4 Already in progress (scan is running)
        #ERROR 11 Invalid argument
        #ERROR 301 Buffer too small
        #ERROR 305 Device not connected
        #ERROR 350 Setting limited by lower limit
        #ERROR 351 Setting limited by upper limit
        #ERROR 352 Setting change not allowed
        #ERROR 353 Zeroswitch not installed
        #ERROR 354 Trigger not installed
        errorTbl = {'ERROR 1': 'Wrong Command',
                    'ERROR 2': 'Requested position too high',
                    'ERROR 3': 'Requested position too low',
                    'ERROR 4': 'Already in progress (scan is running)',
                    'ERROR 11': 'Invalid argument',
                    'ERROR 301': 'Buffer too small',
                    'ERROR 305': 'Device not connected',
                    'ERROR 350': 'Setting limited by lower limit',
                    'ERROR 351': 'Setting limited by upper limit',
                    'ERROR 352': 'Setting change not allowed',
                    'ERROR 353': 'Zeroswitch not installed',
                    'ERROR 354': 'Trigger not installed'}
        
        if errorCode in errorTbl.keys():
            return errorTbl.get(errorCode)
        else:
            return 'Unknown Error Code'

# print usage info
def usage():
    print("\nDescription: Controller for the ETS-Lindgren EMCenter 2-axis Antenna Positioner\n")
    print("\nUsage:\n")
    print(" ",__file__, " [-h] [-p com_port] [-r addr:port]\n")
    print("     -h: help\n")
    print("     -p: specify local comm port to connect to\n")
    print("     -r: specify remote ip and tcp port to connect to\n")
    print("\n")

# main function for command line entry point
def main(argv):
    # grab command line args
    try:
        opts, args = getopt.getopt(argv,"hp:r:", ["--port","--remote"])
    except getopt.GetoptError:
        usage()
        return

    remoteAddr = ('','')
    localPort = ''
    valid = False
    for opt, arg in opts:
        if opt == '-h':
            usage()
            return
        elif opt == '-p':
            if valid == True:
                print('Cannot specify local and remote port!')
                exit(-1)

            localPort = arg
            valid = True
        elif opt == '-r':
            if valid == True:
                print('Cannot specify local and remote port!')
                exit(-1)

            remoteAddr = arg.split(':')
            if len(remoteAddr) < 2:
                print('Must specify remote IP and Port as [ip_addr]:[port]\n')
                usage()
                return
            else:
                valid = True
    
    if not valid:
        usage()
        exit(-1)

    ctrl = EMCenterController(port=localPort, remoteAddr=remoteAddr[0], remotePort=remoteAddr[1])
    ctrl.run()

# callable from command line
if __name__ == "__main__":
    main(sys.argv[1:])
