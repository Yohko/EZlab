# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Keithley 2000 DMM

from PyQt5.QtCore import QThread
import pyvisa
import time

class driver_K2000(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.port = config['dev_port']
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
        self.modes = ['V DC', 'A DC', 'V AC', 'A AC', 'Ω 2W', 'Ω 4W', '°C' , 'Freq', 'Per']
        self.unit = 'V'
        self.mode = config['dev_type']
        self.newmode = [self.mode]
        self.runstate=False
        self.ready = 0
        self.dispbuf = ['']
        self.plotval = [[0.0]]

        value = True
        while value:
            if config['dev_interface'] == 'RS232':
                # just using COMX does not always work
                self.visaport = 'ASRL%s::INSTR' % self.port[3:]
            elif config['dev_interface'][0:4] == 'GPIB':
                self.visaport = '%s::%s::INSTR' % (config['dev_interface'],self.port)

            try:
                rm = pyvisa.ResourceManager()
                self.inst = rm.open_resource(self.visaport)
                if config['dev_interface'] == 'RS232':
                    self.inst.baud_rate = config['dev_baudrate']
                self.inst.query("*IDN?")
                print(' ... Keithley 2000 connected ...')
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
            out = self.inst.query("*IDN?").rstrip()
            if not (out[:len(self.deviceid)] == self.deviceid):
                print('Error. Got IDN:',out,', expected: ',self.deviceid)
                self.error = 1         

        if (self.error == 0):
            self.inst.write("*RST")
            self.inst.write("*CLS")
            self.inst.write(":INITiate")
            self.inst.write(":INITiate:CONTinuous ON")
            time.sleep(1)
            self.switch_mode(config['dev_type'])
            print(' ... done setting up Keithley DMM 2000 ..')


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


    def switch_mode(self, newmode):
        if newmode == 'V DC':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'VOLT:DC'")
            self.inst.write(":SENS:VOLT:DC:RANG:AUTO ON")
            self.inst.write(":SENS:VOLT:DC:AVER:STAT ON")
            self.inst.write(":FORM:ELEM READ")
            self.unit = 'V'
            self.mode = newmode
        elif newmode == 'A DC':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'CURR:DC'")
            self.inst.write(":SENS:CURR:DC:RANG:AUTO ON")
            self.inst.write(":SENS:CURR:DC:AVER:STAT ON")
            self.inst.write(":FORM:ELEM READ")
            self.unit = 'A'
            self.mode = newmode
        if newmode == 'V AC':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'VOLT:AC'")
            self.inst.write(":SENS:VOLT:AC:RANG:AUTO ON")
            self.inst.write(":SENS:VOLT:AC:AVER:STAT ON")
            self.inst.write(":FORM:ELEM READ")
            self.unit = 'V'
            self.mode = newmode
            time.sleep(10)
        elif newmode == 'A AC':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'CURR:AC'")
            self.inst.write(":SENS:CURR:AC:RANG:AUTO ON")
            self.inst.write(":SENS:CURR:AC:AVER:STAT ON")
            self.inst.write(":FORM:ELEM READ")
            self.unit = 'A'
            self.mode = newmode
            time.sleep(10)
        elif newmode == '°C':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'TEMP'")
            self.inst.write(":SENS:TEMP:TC:TYPE J") #J, K, T
            self.inst.write(":SENS:TEMP:AVER:STAT ON")
            self.unit = '°C'
            self.mode = newmode
        elif newmode == 'Ω 2W':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'RES'")
            self.inst.write(":SENS:RES:RANG:AUTO ON")
            self.inst.write(":SENS:RES:AVER:STAT ON")
            self.inst.write(":FORM:ELEM READ")
            self.unit = 'Ω'
            self.mode = newmode
        elif newmode == 'Ω 4W':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'FRES'")
            self.inst.write(":SENS:FRES:RANG:AUTO ON")
            self.inst.write(":SENS:FRES:AVER:STAT ON")
            self.inst.write(":FORM:ELEM READ")
            self.unit = 'Ω'
            self.mode = newmode
        elif newmode == 'Freq':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'FREQ'")
            self.inst.write(":FORM:ELEM READ")
            self.unit = 'Hz'
            self.mode = newmode
        elif newmode == 'Per':
            print(' ... switching to', newmode)
            self.inst.write(":SENS:FUNC 'PER'")
            self.inst.write(":FORM:ELEM READ")
            self.unit = 's'
            self.mode = newmode
        # give it enough time to change settings
        time.sleep(2)

    def run(self):
        self.runstate=True
        while self.runstate:
            if (self.error == 0):
                try:
                    if (self.mode != self.newmode[0]):
                        self.switch_mode(self.newmode[0])

                    self.value = float(self.inst.query(":FETCh?"))
                    readtime = time.time()
                    if(self.save[0]):
                        try:
                            with open(self.savefilename[0],"a") as file_a:
                                file_a.write(str(readtime)+','+str(self.value)+','+self.unit+'\n')
                            file_a.close
                        except Exception:
                            #self.error = 'Error saving K2000'
                            self.save[0] = False                    
                except Exception:
                    print('Connection to K2000 lost.')
                    #self.error = 1
            self.dispbuf[0] = "%.5E %s" % (self.value,self.unit)
            self.plotval[0] = [self.value]
            self.ready = 1
            time.sleep(self.Tdriver)
        self.ready = 0
