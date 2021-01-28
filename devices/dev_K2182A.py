# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Keithley 2182A Nanovoltmeter

from PyQt5.QtCore import QThread
import pyvisa
import time

class driver_K2182A(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.port = config['dev_port']
        self.deviceid = config['dev_id']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.savefilename = [config['dev_savefile']]
        self.unit = 'V'
        self.error = 0
        self.value = 0.0
        self.save = [False]
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
                print(' ... Keithley 2182A connected ...')
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
            out = self.inst.query("*IDN?").rstrip()
            if not (out[:len(self.deviceid)] == self.deviceid):
                print('Error. Got IDN:',out,', expected: ',self.deviceid)
                self.error = 1

        if (self.error == 0):
            # reset Keithley and change settings
            self.inst.write("*RST")
            self.inst.write("*CLS")
            self.inst.write(":INITiate")
            self.inst.write(":INITiate:CONTinuous ON")
            self.inst.write("SENS:FUNC 'VOLT:DC'")
            self.inst.write("SENS:CHAN 1")
            self.inst.write("SENS:VOLT:CHAN1:RANG:AUTO ON")
            self.inst.write("SENS:VOLT:CHAN2:RANG:AUTO ON")
            print(' ... done setting up Keithley NVM 2182A ..')


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
                    self.value = float(self.inst.query(":FETCh?"))
                    readtime = time.time()
                    if(self.save[0]):
                        try:
                            with open(self.savefilename[0],"a") as file_a:
                                file_a.write(str(readtime)+','+str(self.value)+'\n')
                            file_a.close
                        except Exception:
                            #self.error = 'Error saving K2182A'
                            self.save[0] = False                    
                except Exception:
                    print('Connection to K2182A lost.')
                    self.error = 1
            self.dispbuf[0] = "%.5E %s" % (self.value,self.unit)
            self.plotval[0] = [self.value]
            self.ready = 1
            time.sleep(self.Tdriver)
        self.ready = 0
