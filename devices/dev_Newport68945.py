# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Newport 68945 Digital Exposure Controller

from PyQt5.QtCore import QThread
import pyvisa
import time

class driver_Newport68945(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.port = config['dev_port']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.error = 0
        self.state = False
        self.newstate = [False]
        value = True

        while value:
            if config['dev_interface'] == 'RS232':
                # just using COMX does not always work
                self.visaport = 'ASRL%s::INSTR' % self.port[3:]
            try:
                rm = pyvisa.ResourceManager()
                self.inst = rm.open_resource(self.visaport)
                if config['dev_interface'] == 'RS232':
                    self.inst.baud_rate = config['dev_baudrate']
                    self.inst.write_termination = '\r'
                    self.inst.read_termination = '\r\n'
                print(' ... Newport68945 connected ...')
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
            try:
                test = int(self.inst.query('RUN?').rstrip())
                if (test == 0):
                    print('Shutter is closed')
                    self.state = False
                elif (test == 1):
                    print('Shutter is open')
                    self.state = True                
                else:
                    print('Shutter is closed')
                    self.state = False
                self.newstate[0] = self.state

                _ = self.inst.query('EXPSTATE?')
            except Exception:
                print('Serial Error Newport68945 ...')
                self.error = 1


    def __del__(self):
        self.wait()


    def run(self):
        state=True
        while state:
            if (self.error == 0):
                try:
                    if (self.state!=self.newstate[0]):
                        self.state = self.newstate[0]
                        if self.newstate[0]:
                            print('open Shutter')
                            _ = self.inst.query('start')
                        else:
                            print('close Shutter')
                            _ = self.inst.query('stop')
                except Exception:
                    print('Connection to Newport68945 lost.')
                    self.error = 1
            time.sleep(self.Tdriver)
