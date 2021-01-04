# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Newport 68945 Digital Exposure Controller

from PyQt5.QtCore import QThread
import serial
import time

class driver_Newport68945(QThread):

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
                self.serNewport68945 = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... Newport68945 Serial connected ...')
                value = False
            except Exception:
                print('Serial Error Newport68945 ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False
        if (self.error == 0):
            self.serNewport68945.close()
            self.serNewport68945.open()
            if not self.serNewport68945.isOpen():
                print('Serial port error')
                self.error = 1
            try:
                self.serNewport68945.write(str.encode('RUN?\r'))
                time.sleep(0.5)
                out=''
                out = self.serNewport68945.read(self.serNewport68945.in_waiting)
                out = out.rstrip()
                test = int(out)
                if (test == 0):
                    print('Shutter is closed')
                    self.tate = False
                elif (test == 1):
                    print('Shutter is open')
                    self.state = True                
                else:
                    print('Shutter is closed')
                    self.state = False
                self.newstate[0] = self.state

                self.serNewport68945.write(str.encode('EXPSTATE?\r'))
                time.sleep(0.5)
                out=''
                out = self.serNewport68945.read(self.serNewport68945.in_waiting)
            except Exception:
                print('Serial Error Newport68945 ...')
                self.error = 1


    def __del__(self):
        print('Terminate Newport68945')
        self.wait()


    def run(self):
        state=True
        while state:
            if (self.error == 0):
                try:
                    if (self.state!=self.newstate[0]):
                        self.state = self.newstate[0]
                        if self.newstate[0]:
                            self.serNewport68945.write(str.encode('start\r'))
                            time.sleep(0.5)
                            out=''
                            out = self.serNewport68945.read(self.serNewport68945.in_waiting)
                            print(out)
                        else:
                            self.serNewport68945.write(str.encode('stop\r'))
                            time.sleep(0.5)
                            out=''
                            out = self.serNewport68945.read(self.serNewport68945.in_waiting)
                            print(out)
                except Exception:
                    print('Connection to Newport68945 lost.')
                    self.error = 1
            time.sleep(self.Tdriver)
