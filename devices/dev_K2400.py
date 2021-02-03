# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Keithley 2400 Sourcemeter
# K2440

from PyQt5.QtCore import QThread
import pyvisa
import time

class driver_K2400(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.port = config['dev_port']
        self.deviceid = config['dev_id']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.savefilename = [config['dev_savefile']]
        self.error = 0
        self.value = [0.0, 0.0]
        self.state = False # on or off
        self.newstate = [self.state] # on or off
        self.save = [False]
        self.modes = ['V', 'A']
        self.mode = config['dev_type']
        self.newmode = [self.mode]
        self.unit = ''
        self.setP = config['dev_setP']
        self.newsetP = [self.setP]
        self.compliance = config['dev_compliance']
        self.newcompliance = [self.compliance]
        self.runstate=False
        self.ready = 0
        self.dispbuf = ['']
        self.plotval = [[0.0]]

        # connect to device
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
                print(' ... Keithley 2400 connected ...')
                value = False
            except Exception:
                print('Serial Error K2400 ...')
                if self.retry:
                    print(' ... trying again in a few seconds ...')
                    time.sleep(self.Tretry)
                    value = True
                else:
                    self.error = 1
                    value = False

        # check device ID
        if (self.error == 0):
            print(' ... setting up Keithley 2400, please wait ..')
            out = self.inst.query("*IDN?").rstrip()
            if not (out[:len(self.deviceid)] == self.deviceid):
                print('Error. Got IDN:',out,', expected: ',self.deviceid)
                self.error = 1

        # initialize device
        if (self.error == 0):
            self.inst.write(":OUTP OFF")
            self.inst.write("*RST")
            self.switch_mode(self.mode)
            self.set_val(self.setP)
            print(' ... done setting up Keithley 2400 ..')


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
        if newmode == 'V':
            print(' ... switching to',newmode)
            self.inst.write(":OUTP OFF")
            self.unit = 'A' # set V and measure A
            self.inst.write(":SOUR:FUNC VOLT")
            self.inst.write(":SENS:FUNC 'CURR'")
            self.inst.write(":SENS:CURR:PROT %f" % self.compliance) # 1 A max
            self.inst.write(":FORM:ELEM VOLT,CURR") # V and A reading
            self.inst.write(":ROUT:TERM FRON")
            self.mode = newmode
        elif newmode == 'A':
            print(' ... switching to',newmode)
            self.inst.write(":OUTP OFF")
            self.unit = 'V' # set V and measure A
            self.inst.write(":SOUR:FUNC CURR")
            self.inst.write(":SENS:FUNC 'VOLT'")
            self.inst.write(":SENS:VOLT:PROT %f" % self.compliance) # 5 V max
            self.inst.write(":FORM:ELEM VOLT,CURR") # V and A reading
            self.inst.write(":ROUT:TERM FRON")
            self.mode = newmode
        # give it enough time to change settings
        time.sleep(2)


    def set_val(self, val):
        if self.mode == 'V':
            self.inst.write(":SOUR:VOLT %f" % val)  
            self.setP = val
        elif self.mode == 'A':
            self.inst.write(":SOUR:CURR %f" % val) 
            self.setP = val


    def set_compliance(self, val):
        if self.mode == 'A':
            self.inst.write(":SENS:VOLT:PROT %f" % val)
            self.compliance = val
        elif self.mode == 'V':
            self.inst.write(":SENS:CURR:PROT %f" % val) 
            self.compliance = val


    def switch_on(self):
        self.inst.write(":OUTP ON")
        self.state = True # on or off
        print('turn on Keithley 2400')

    def switch_off(self):
        self.inst.write(":OUTP OFF")
        self.state = False # on or off
        self.value[0] = 0
        self.value[1] = 0
        print('turn off Keithley 2400')


    def run(self):
        self.runstate=True
        while self.runstate:
            if (self.error == 0):
                try:
                    if (self.compliance != self.newcompliance[0]):
                        self.set_compliance(self.newcompliance[0])

                    if (self.mode != self.newmode[0]):
                        # switching mode turns output off
                        self.switch_mode(self.newmode[0])


                    if (self.setP!=self.newsetP[0]):
                        self.set_val(self.newsetP[0])

                    if (self.state!=self.newstate[0]):
                        if self.newstate[0]:
                            self.switch_on()
                        else:
                            self.switch_off()

                    # is output on?
                    if self.state:
                        out = self.inst.query(":READ?").rstrip().split(',')
                        readtime = time.time()
                        if len(out) == 2:
                            self.value = [float(i) for i in out]
                        elif len(out) == 1:
                            # e.g. for pulsed mode
                            if self.mode == 'V':
                                self.value[0] = self.setP
                                self.value[1] = out[0]
                            elif self.mode == 'A':
                                self.value[0] = out[0]
                                self.value[1] = self.setP
                        if(self.save[0]):
                            try:
                                with open(self.savefilename[0],"a") as file_a:
                                    file_a.write(str(readtime)+','+str(self.value[0])+','+str(self.value[1])+'\n')
                                file_a.close
                            except Exception:
                                #self.error = 'Error saving K2400'
                                print('Error saving K2400.')
                                self.save[0] = False
                except Exception:
                    print('Connection to K2400 lost.')
                    self.error = 1
            if self.mode == 'V':
                self.dispbuf[0] = "%f %s" % (self.out[1],self.unit)
                self.plotval[0] = [self.value[1]]
            elif self.mode == 'A':
                self.dispbuf[0] = "%f %s" % (self.out[0],self.unit)
                self.plotval[0] = [self.value[0]]
            self.ready = 1
            time.sleep(self.Tdriver)
        self.ready = 0
