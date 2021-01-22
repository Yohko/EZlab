# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# SRS PTC10 — Programmable temperature controller
# https://www.thinksrs.com/downloads/pdfs/manuals/PTC10m.pdf

from PyQt5.QtCore import QThread
import serial
import time

class driver_PTC10(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.serialport = config['dev_port']
        self.baudrate = config['dev_baudrate']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.dev_type = config['dev_type']
        self.savefilename = config['dev_savefile']
        self.error = 0
        self.val = ['' for i in range(len(self.dev_type))]
        self.save = [False for i in range(len(self.dev_type))]
        self.valames = ['' for i in range(len(self.dev_type))]
        value = True
        while value:
            try:
                self.ser = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... PTC10 Serial connected ...')
                value = False
            except Exception:
                print('Serial Error PTC10 ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False
        if (self.error == 0):
            self.ser.close()
            self.ser.open()
            if not self.ser.isOpen():
                print('Serial port error')
                self.error = 1

        if (self.error == 0):
            self.ser.write(str.encode(' getOutputNames?\r\n'))
            time.sleep(0.5)
            out=''
            out = self.ser.read(self.ser.in_waiting)
            out = out.rstrip()
            out = out.decode('ASCII').rstrip().split(",")
            self.valnames = [out[i-1] for i in self.dev_type]
            print(' ...',self.valnames)
 

    def __del__(self):
        print('Terminate PTC10')
        self.wait()


    def run(self):
        state=True
        while state:
            if (self.error == 0):
                try:
                    self.ser.write(str.encode('getOutput?\r\n'))
                    # wait one second before reading output. 
                    time.sleep(0.5)
                    out=''
                    out = self.ser.read(self.ser.in_waiting)
                    out = out.rstrip()
                    tmptime = time.time()
                    try:
                        self.values = out.decode('ASCII').rstrip().split(",")
                        self.val = [self.values[i-1] for i in self.dev_type]
                    except Exception:
                        self.val = ["" for i in range(len(self.dev_type))]

                    for deviceidx, tmpvalue in enumerate(self.save):
                        if(tmpvalue):
                            try:
                                with open(self.savefilename[deviceidx],"a") as file_a:
                                    file_a.write(str(tmptime)+','+self.val[deviceidx]+'\n')
                                file_a.close
                            except Exception:
                                self.save[deviceidx] = False
                except Exception:
                    print('Connection to PTC10 lost.')
                    self.error = 1
            time.sleep(self.Tdriver)
