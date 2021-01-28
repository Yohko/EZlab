# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# https://www.sutter.com/manuals/LBSC_OpMan.pdf

from PyQt5.QtCore import QThread
import serial
import time

class driver_LambdaSC(QThread):

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
        self.runstate=False
        self.ready = 0
        self.dispbuf = ['']
        self.plotval = [[0.0]]

        value = True
        while value:
            try:
                self.serLambdaSC = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... LambdaSC Serial connected ...')
                value = False
            except Exception:
                print('Serial Error LambdaSC ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False
        if (self.error == 0):
            self.serLambdaSC.close()
            self.serLambdaSC.open()
            if not self.serLambdaSC.isOpen():
                print('Serial port error')
                self.error = 1
            try:
                time.sleep(0.5)
                out=''
                out = self.serLambdaSC.read(self.serLambdaSC.in_waiting)
                self.serLambdaSC.write(b'\xCC') # Factory reset
                time.sleep(0.5)
                out=''
                out = self.serLambdaSC.read(self.serLambdaSC.in_waiting)
                out = out.rstrip()
                print(out[1:2])
                if (out[1:2] == b'\xac'):
                    self.state = False
                    print('Shutter is closed')
                elif (out[1:2] == b'\xaa'):
                    self.state = True
                    print('Shutter is open')
                else:
                    print('Serial Error LambdaSC 0 ...')
                    self.error = 1
                self.newstate[0] = self.state
            except Exception:
                print('Serial Error LambdaSC ...')
                self.error = 1


    def __del__(self):
        if self.ready !=0:
            self.stop()
            self.wait()


    def stop(self):
        self.runstate=False
        time.sleep(self.Tdriver)
        while(self.ready !=0):
            print(' ... waiting for shutdown')
            time.sleep(0.1)


    def run(self):
        self.runstate=True
        while self.runstate:
            if (self.error == 0):
                try:
                    if (self.state!=self.newstate[0]):
                        self.state = self.newstate[0]
                        if self.newstate[0]:
                            # TTL IN Pulse trigger disabled (necessary)
                            self.serLambdaSC.write(b'\xFA\xA0')
                            # open shutter
                            self.serLambdaSC.write(b'\xAA')
                            # TTL IN High Triggers SmartShutter to Open
                            self.serLambdaSC.write(b'\xFA\xA1')
                            print('Shutter open')
                            time.sleep(0.1)
                            self.serLambdaSC.read(self.serLambdaSC.in_waiting)
                        else:
                            # TTL IN Pulse trigger disabled (necessary)
                            self.serLambdaSC.write(b'\xFA\xA0')
                            # open shutter
                            self.serLambdaSC.write(b'\xAC')
                            # TTL IN High Triggers SmartShutter to Open 
                            self.serLambdaSC.write(b'\xFA\xA1')
                            print('Shutter closed')
                            time.sleep(0.1)
                            self.serLambdaSC.read(self.serLambdaSC.in_waiting)
                except Exception:
                    print('Connection to LambdaSC lost.')
                    self.error = 1
            self.ready = 1
            time.sleep(self.Tdriver)
        self.ready = 0
