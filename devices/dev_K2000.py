# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Keithley 2000 DMM

from PyQt5.QtCore import QThread
import serial
import time

class driver_K2000(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.serialport = config['dev_port']
        self.baudrate = config['dev_baudrate']
        self.deviceid = config['dev_id']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.savefilename = [config['dev_savefile']]


        self.error = 0
        self.value = 0.0
        self.sensesett = "VOLT"
        self.ACDC = "DC"
        self.save = [False]
        value = True
        while value:
            try:
                self.ser = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... K2000 Serial connected ...')
                value = False
            except Exception:
                print('Serial Error K2000 ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False
        if (self.error == 0):
            print(' ... setting up Keithley DMM 2000, please wait ..')
            self.ser.close()
            self.ser.open()
            self.ser.write(str.encode('*IDN?\r\n'))
            time.sleep(1)
            out = self.ser.read(self.ser.in_waiting)
            out = out.rstrip()
            out = out.decode('ASCII')
            if not (out[:len(self.deviceid)] == self.deviceid):
                print('Error. Got IDN:',out,', expected: ',self.deviceid)
                self.error = 1

        if (self.error == 0):
            self.ser.write(str.encode('*RST\r\n'))
            self.ser.write(str.encode(':INITiate\r\n'))
            self.ser.write(str.encode(':INITiate:CONTinuous ON\r\n'))
            time.sleep(1)
            self.ser.write(str.encode("SENS:FUNC '"+self.sensesett+":"+self.ACDC+"'\r\n"))
            self.ser.write(str.encode(":SENS:"+self.sensesett+":"+self.ACDC+":RANG:AUTO ON\r\n"))
            self.ser.write(str.encode(":SENS:"+self.sensesett+":"+self.ACDC+":AVER:STAT ON\r\n"))
            # only DC
            #self.ser.write(str.encode(":SENS:"+sensesett+":"+ACDC+":NPLC 1\r\n")) # 0.01..10 power cycles per integration
            self.ser.write(str.encode(':FORM:ELEM READ\r\n'))
            time.sleep(5) # give it enough time to change settings
            print(' ... done setting up Keithley DMM 2000 ..')


    def __del__(self):
        print('Terminate K2000')
        self.wait()


    def run(self):
        state=True
        while state:
            if (self.error == 0):
                try:
                    self.ser.write(str.encode(':FETCh?\r\n'))
                    # wait one second before reading output. 
                    time.sleep(1)
                    out=''
                    out = self.ser.read(self.ser.in_waiting)
                    self.value = float(out.decode('ASCII'))
                    if(self.save[0]):
                        try:
                            with open(self.savefilename[0],"a") as file_a:
                                file_a.write(str(time.time())+','+str(self.value)+'\n')
                            file_a.close
                        except Exception:
                            #self.error = 'Error saving K2000'
                            self.save[0] = False                    
                except Exception:
                    print('Connection to K2000 lost.')
                    self.error = 1
            time.sleep(self.Tdriver)
