# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Keithley 2182A Nanovoltmeter

from PyQt5.QtCore import QThread
import serial
import time

class driver_K2182A(QThread):

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
        self.sensesett = "VOLT" # 'VOLT' or 'TEMP'
        self.save = [False]
        value = True
        while value:
            try:
                self.serK2182A = serial.Serial(
                    port=self.serialport,
                    baudrate=self.baudrate
                )
                print(' ... K2182A Serial connected ...')
                value = False
            except Exception:
                print('Serial Error K2182A ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False
        if (self.error == 0):
            print(' ... setting up Keithley NVM 2182A, please wait ..')
            self.serK2182A.close()
            self.serK2182A.open()
            if not self.serK2182A.isOpen():
                print('Serial port error')
                self.error = 1
        if (self.error == 0):
            self.serK2182A.write(str.encode('*IDN?\r\n'))
            time.sleep(1)
            out = self.serK2182A.read(self.serK2182A.in_waiting)
            out = out.rstrip()
            out = out.decode('ASCII')
            if not (out[:len(self.deviceid)] == self.deviceid):
                print('Error. Got IDN:',out,', expected: ',self.deviceid)
                self.error = 1
        if (self.error == 0):
            # reset Keithley and change settings
            self.serK2182A.write(str.encode('*RST\r\n'))
            self.serK2182A.write(str.encode('*CLS\r\n'))
            self.serK2182A.write(str.encode(':INITiate\r\n'))
            self.serK2182A.write(str.encode(':INITiate:CONTinuous ON\r\n'))
            self.serK2182A.write(str.encode("SENS:FUNC '"+self.sensesett+":DC'\r\n"))
            self.serK2182A.write(str.encode("SENS:CHAN 1\r\n"))
            self.serK2182A.write(str.encode("SENS:VOLT:CHAN1:RANG:AUTO ON\r\n"))
            self.serK2182A.write(str.encode("SENS:VOLT:CHAN2:RANG:AUTO ON\r\n"))
            # give it enough time to change settings
            time.sleep(5)
            print(' ... done setting up Keithley NVM 2182A ..')


    def __del__(self):
        print('Terminate K2182A')
        self.wait()


    def run(self):
        state=True
        while state:
            if (self.error == 0):
                try:
                    self.serK2182A.write(str.encode(':FETCh?\r\n'))
                    # wait one second before reading output. 
                    time.sleep(1)
                    out=''
                    out = self.serK2182A.read(self.serK2182A.in_waiting)
                    self.value = float(out.decode('ASCII'))
                    if(self.save[0]):
                        try:
                            with open(self.savefilename[0],"a") as file_a:
                                file_a.write(str(time.time())+','+str(self.value)+'\n')
                            file_a.close
                        except Exception:
                            #self.error = 'Error saving K2182A'
                            self.save[0] = False                    
                except Exception:
                    print('Connection to K2182A lost.')
                    self.error = 1
            time.sleep(self.Tdriver)
