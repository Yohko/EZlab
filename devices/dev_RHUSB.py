# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Omega RH-USB
# https://assets.omega.com/manuals/test-and-measurement-equipment/temperature/sensors/rtds/M4707.pdf

from PyQt5.QtCore import QThread
import serial
import time

class driver_RHUSB(QThread):


    def __init__(self, config):
        QThread.__init__(self)
        self.serialport = config['dev_port']
        self.baudrate = config['dev_baudrate']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.savefilename = [config['dev_savefile']]
        self.error = 0
        self.valuetemp = ''
        self.valueRH = ''
        self.save = [False]
        value = True
        while value:
            try:
                self.serRHUSB = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... RHUSB Serial connected ...')
                value = False
            except Exception:
                print('Serial Error RHUSB ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False
        if (self.error == 0):
            self.serRHUSB.close()
            self.serRHUSB.open()
            if not self.serRHUSB.isOpen():
                print('Serial port error')
                self.error = 1
            # get a dummy reading
            self.serRHUSB.write(str.encode('C\r\n'))
            # wait one second before reading output. 
            time.sleep(0.5)
            self.serRHUSB.read(self.serRHUSB.in_waiting)


    def __del__(self):
        print('Terminate RHUSB')
        self.wait()


    def run(self):
        state=True
        while state:
            if (self.error == 0):
                try:
                    self.serRHUSB.write(str.encode('C\r\n'))
                    # wait one second before reading output. 
                    time.sleep(0.5)
                    out=''
                    out = self.serRHUSB.read(self.serRHUSB.in_waiting)
                    out = out.rstrip()
                    try:
                        self.valuetemp = out.decode('ASCII')
                        self.valuetemp = self.valuetemp.rstrip()
                        self.valuetemp = self.valuetemp[:-3:]
                    except Exception:
                        self.valuetemp = '-1'
                    time.sleep(0.2)

                    self.serRHUSB.write(str.encode('H\r\n'))
                    # wait one second before reading output. 
                    time.sleep(0.5)
                    out=''
                    out = self.serRHUSB.read(self.serRHUSB.in_waiting)
                    out = out.rstrip()
                    try:
                        self.valueRH = out.decode('ASCII')
                        self.valueRH = self.valueRH.rstrip()
                        self.valueRH = self.valueRH[:-3:] #
                    except Exception:
                        self.valueRH = '-1'
                    if(self.save[0]):
                        try:
                            with open(self.savefilename[0],"a") as file_a:
                                file_a.write(str(time.time())+','
                                             +self.valueRH[:-4:]
                                             +','+str(self.valuetemp[:-2:])
                                             +'\n')
                            file_a.close
                        except Exception:
                            #self.error = 'Error saving RHUSB'
                            self.save[0] = False      
                except Exception:
                    print('Connection to RHUSB lost.')
                    self.error = 1
            time.sleep(self.Tdriver)
   