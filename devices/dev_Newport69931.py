# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

from PyQt5.QtCore import QThread
import serial
import time

class driver_Newport69931(QThread):
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

        value = True
        while value:
            try:
                self.serNewport69931 = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... Newport69931 Serial connected ...')
                value = False
            except Exception:
                print('Serial Error Newport69931 ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False
        if (self.error == 0):
            self.serNewport69931.close()
            self.serNewport69931.open()
            if not self.serNewport69931.isOpen():
                print('Serial port error')
                self.error = 1
            try:
                self.serNewport69931.write(str.encode('STB?\r\n'))
                time.sleep(0.5)
                out=''
                out = self.serNewport69931.read(self.serNewport69931.in_waiting)
                out = out.rstrip()
                test = bin(int(out[3:],16))
                if (len(test)<10):
                    print('Lamp is off')
                    self.state = False
                elif (test[9] == '1'):
                    print('Lamp is on')
                    self.state = True                
                else:
                    print('Lamp is off')
                    self.state = False
                self.newstate[0] = self.state
            except Exception:
                print('Serial Error Newport69931 ...')
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
                            self.serNewport69931.write(str.encode('START\r\n'))
                            time.sleep(3600)
                        else:
                            self.serNewport69931.write(str.encode('STOP\r\n'))
                            time.sleep(3600)
                except Exception:
                    print('Connection to Newport69931 lost.')
                    self.error = 1
            self.ready = 1
            time.sleep(self.Tdriver)
        self.ready = 0
