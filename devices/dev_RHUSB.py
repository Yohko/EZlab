# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# Omega RH-USB
# https://assets.omega.com/manuals/test-and-measurement-equipment/temperature/sensors/rtds/M4707.pdf

from PyQt5.QtCore import QThread
import pyvisa
import time

class driver_RHUSB(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.port = config['dev_port']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.savefilename = [config['dev_savefile']]
        self.error = 0
        self.valueTemp = ''
        self.valueRH = ''
        self.save = [False]
        self.runstate=False
        self.ready = 0
        self.dispbuf = ['']
        self.plotval = [[0.0],[0.0]]

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
                print(' ... RHUSB connected ...')
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
            # get a dummy reading
            _ = self.inst.query('C')


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
                    self.valueTemp = self.inst.query('C').rstrip()
                    try:
                        self.valueTemp = self.valueTemp[:-2].rstrip()
                    except Exception:
                        self.valueTemp = '-1'

                    self.valueRH = self.inst.query('H').rstrip()
                    try:
                        self.valueRH = self.valueRH[:-3].rstrip()
                    except Exception:
                        self.valueRH = '-1'

                    if(self.save[0]):
                        try:
                            with open(self.savefilename[0],"a") as file_a:
                                file_a.write(str(time.time())
                                             +','+self.valueRH.replace('>','')
                                             +','+self.valueTemp.replace('>','')
                                             +'\n')
                            file_a.close
                        except Exception:
                            #self.error = 'Error saving RHUSB'
                            self.save[0] = False      
                except Exception:
                    print('Connection to RHUSB lost.')
                    self.error = 1
            self.dispbuf[0] = "%s °C, %s %%RH" % (self.valueTemp,self.valueRH)

            try:
                rh=float(self.valueRH.replace('>',''))
                T=float(self.valueTemp.replace('>',''))
            #         water = (6.112*math.exp((17.67*T)/(T+243.5))*rh*2.1674)/ (273.15+T)
            #         MW = 18.01528 # water
            #         #Vm = 22.71108
            #         Vm = 24.5
            #         #At Standard Temperature and Pressure (STP, 0°C and 1 atm) the molar volume –1
            #         # of a gas is 22.4 L mol
            #         #At Standard Laboratory Conditions (SLC, 25°C and 1 atm) the molar volume –1
            #         # of a gas is 24.5 L mol
            #         ppm = 1000*Vm/MW*water
            except Exception:
                rh = 0.0
                T = 0.0
            self.plotval[0] = [rh, T]


            self.ready = 1
            time.sleep(self.Tdriver)
        self.ready = 0
