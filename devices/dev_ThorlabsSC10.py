# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Thorlabs SC10 - Optical Beam Shutter Controller
# https://www.thorlabs.com/drawings/89b89b10a35f18c8-85A29D67-0B50-A101-99C61CA07608B8C2/SC10-Manual.pdf

from PyQt5.QtCore import QThread
import serial
import time

class driver_ThorlabsSC10(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.serialport = config['dev_port']
        self.baudrate = config['dev_baudrate']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.error = 0
        self.state = False
        self.newstate = [False]
        value = True
        while value:
            try:
                self.serThorlabsSC = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... ThorlabsSC Serial connected ...')
                value = False
            except Exception:
                print('Serial Error ThorlabsSC ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False
        if (self.error == 0):
            self.serThorlabsSC.close()
            self.serThorlabsSC.open()
            if not self.serThorlabsSC.isOpen():
                print('Serial port error')
                self.error = 1
            try:
                self.serThorlabsSC.write(str.encode('id?\r'))
                time.sleep(0.5)
                out=''
                out = self.serThorlabsSC.read(self.serThorlabsSC.in_waiting)
                # get shutter status
                self.serThorlabsSC.write(str.encode('ens?\r'))
                time.sleep(0.5)
                out=''
                out = self.serThorlabsSC.read(self.serThorlabsSC.in_waiting)
                out = out.rstrip()
                print(out)
                if (out == b'ens?\r0\r>'):
                    self.state = False
                    print('Shutter is open')
                elif (out == b'ens?\r1\r>'):
                    self.state = True
                    print('Shutter is closed')
                else:
                    print('Serial Error ThorlabsSC ...')
                    self.error = 1
                self.newstate[0] = self.state
            except Exception:
                print('Serial Error ThorlabsSC ...')
                self.error = 1


    def __del__(self):
        print('Terminate ThorlabsSC')
        self.wait()


    def run(self):
        state=True
        while state:
            if (self.error == 0):
                try:
                    # get shutter status
                    self.serThorlabsSC.write(str.encode('ens?\r'))
                    time.sleep(0.1)
                    out=''
                    out = self.serThorlabsSC.read(self.serThorlabsSC.in_waiting)
                    out = out.rstrip()
                    if (out == b'ens?\r0\r>'):
                        self.state = False
                    elif (out == b'ens?\r1\r>'):
                        self.state = True                    
                    else:
                        print('ThorlabsSC Error.')
                        self.error = 1
                    if (self.state!=self.newstate[0]):
                        self.state = self.newstate[0]
                        # get shutter status
                        self.serThorlabsSC.write(str.encode('ens\r'))
                        time.sleep(0.1)
                        out=''
                        out = self.serThorlabsSC.read(self.serThorlabsSC.in_waiting)
                        print('Shutter triggered')
                except Exception:
                    print('Connection to ThorlabsSC lost.')
                    self.error = 1
            time.sleep(self.Tdriver)
