# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Keithley 2100 Series: 6½-Digit USB Multimeter
# only USB interface

from PyQt5.QtCore import QThread
import pyvisa
import time

class driver_K2100(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.deviceid = config['dev_id']
        self.deviceport = config['dev_port']
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
                    rm = pyvisa.ResourceManager()
                    self.inst = rm.open_resource(self.deviceport)
                    self.inst.query("*IDN?")
                    print(' ... K2100 Serial connected ...')
                    value = False
            except Exception:
                    print('Error connecting K2100 ...')
                    if self.retry:
                        print(' ... trying again in a few seconds ...')
                        time.sleep(self.Tretry)
                        value = True
                    else:
                        self.error = 1
                        value = False
        if (self.error == 0):
            print(' ... setting up Keithley DMM 2100, please wait ..')
            out = self.inst.query("*IDN?")
            out = out.rstrip()
            if not (out[:len(self.deviceid)] == self.deviceid):
                print('Error. Got IDN:',out,', expected: ',self.deviceid)
                self.error = 1         
        if (self.error == 0):
            self.inst.write('*RST')
            self.inst.write('SENS:FUNC "VOLT:DC"')
            self.inst.write('SENS:VOLT:DC:RANG:AUTO ON')
            #print(self.inst.write('SENS:VOLT:DC:RES MIN')) # MIN selects the smallest value accepted, which gives the most resolution. 
            #print(self.inst.write('SENS:VOLT:DC:NPLC 1')) # 0.01..10 power cycles per integration
            #print(self.inst.write('TRIG:SOUR IMM'))
            #print(self.inst.write('TRIG:COUN INF'))
            #print(self.inst.write('INIT'))
            #print(self.inst.write(':INITiate:CONTinuous ON'))
            time.sleep(1)
            #print(self.inst.write("SENS:FUNC '"+self.sensesett+":"+self.ACDC+"'"))
            #print(self.inst.write(":SENS:"+self.sensesett+":"+self.ACDC+":RANG:AUTO ON"))
            #print(self.inst.write(":SENS:"+self.sensesett+":"+self.ACDC+":AVER:STAT ON"))
            # only DC
            #self.ser.write(str.encode(":SENS:"+sensesett+":"+ACDC+":NPLC 1\r\n")) # 0.01..10 power cycles per integration
            #print(self.inst.write(':FORM:ELEM READ'))
            time.sleep(5) # give it enough time to change settings
            print(' ... done setting up Keithley DMM 2100 ..')
            
            
    def __del__(self):
        print('Terminate K2100')
        self.wait()


    def run(self):
        state=True
        while state:
            if (self.error == 0):
                try:
                    out = self.inst.query('READ?')
                    # wait one second before reading output.
                    self.value = float(out)
                    if(self.save[0]):
                        try:
                            with open(self.savefilename[0],"a") as file_a:
                                file_a.write(str(time.time())+','+str(self.value)+'\n')
                            file_a.close
                        except Exception:
                            #self.error = 'Error saving K2000'
                            self.save[0] = False                    
                except Exception:                        
                    print('Connection to K2100 lost.')
                    #self.error = 1
            time.sleep(self.Tdriver)
