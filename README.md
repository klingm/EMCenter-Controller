# EMCenter-Controller
This program controls the EMCenter 2-Axis Antenna Positioner using the USB interface on the EMCenter controller.

The program consists of two executable scripts.  The first script(tcp_serial_redirect.py)  implements a TCP to serial "pipe" to allow an arbitrary remote computer to send commands and receive status from the EMCenter controller hardware.  This executable must be run on a computer that is physically connected to the controller via USB and also that is physically connected to an accessible network.  The second script (emcenter_ctrl.py) implements the user interface and all control logic.  This program can be run on an arbitrary computer system that is connected to the same network as previous system.  It then sends and receives network commands/status to control the antenna positioner.

The emcenter_ctrl.py script can also be imported as a module into other Python programs in order to allow them to remotely control the ETS-Lindgren 2-axis antenna positioner.  When used in this way there is no user interface.

## Hardware requirements
In order to run this program the following is required for each system:

### USB Interface Computer
Windows 10
Python3 (w/ pyserial installed)

### EMCenter-Controller Computer
Windows 10, Ubuntu Linux (>= 20.04)
Python3 (w/ Matplotlib, PySimpleGUI, pyserial installed)

## User Interface
The user interface is shown below.

![EMCenter Positioner GUI](readme/gui.png)
