# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Sper Scientific 800005 TYPE K J Thermometer
# uses 5V TTL Serial

from PyQt5.QtCore import QThread
import serial
import time

# Commands:
# K: Model Nr (4bytes)
# D: Main display, range, data, unit (22 bytes)
# B: Secondarey display, range, data, unit (22 bytes)
# S: Status (13bytes)
# H: Hold button
# T: Timer button
# M: AVG/MAX/MIN button
# N: Exit AVG/MAX/MIN mode
# R: Rel button
# C: */* button
# A: all encoded data (8byte)


class driver_SPERSCI80005(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.serialport = config['dev_port']
        self.baudrate = config['dev_baudrate']
        self.deviceid = config['dev_id']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.dev_type = config['dev_type']
        self.savefilename = [config['dev_savefile']]
        self.error = 0
        self.value = ''
        self.unit = ''
        self.save = [False]
        self.runstate=False
        self.ready = 0
        self.dispbuf = ['']
        self.plotval = [[0.0]]

        value = True
        while value:
            try:
                self.ser = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... SPERSCI80005 connected ...')
                value = False
            except Exception:
                print('Serial Error SPERSCI80005 ...')
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

        # model number check
        MNr = self.ser_query('K')
        if not MNr[0:3] == self.deviceid:
                print('Error. Got IDN:',MNr,', expected: ',self.deviceid)
                self.error = 1   


    def ser_query(self, q):
        if (self.error == 0):
            self.ser.write(str.encode('%s\r' % q))
            time.sleep(0.3)
            out = self.ser.read(self.ser.in_waiting).decode('ASCII').rstrip()
        else:
            out = ''
        return out


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
                    readtime = time.time()                   
                    Maindisp = self.ser_query('D').replace(' ','')
                    if len(Maindisp) == 0:
                        continue
                    Secdisp = self.ser_query('B').replace(' ','')
                    if len(Secdisp) == 0:
                        continue
                    self.unit = Maindisp[-1:]
                    self.value = Maindisp[:-1]
                    if(self.save[0]):
                        try:
                            with open(self.savefilename[0],"a") as file_a:
                                file_a.write(str(readtime)+','+Maindisp[:-1]+','+self.unit+','+Secdisp[:-5]+','+Secdisp[-5:]+'\n')
                            file_a.close
                        except Exception:
                            self.save[0] = False
                    self.dispbuf[0] = "%s °%s; %s" % (self.value, self.unit, Secdisp[:-5])
                    self.plotval[0] = [float(self.value)]
                except Exception:
                    print('Connection to SPERSCI80005 lost.')
                    self.error = 1
            self.ready = 1
            time.sleep(self.Tdriver)
        self.ready = 0
