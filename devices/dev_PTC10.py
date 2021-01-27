# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# SRS PTC10 — Programmable temperature controller
# https://www.thinksrs.com/downloads/pdfs/manuals/PTC10m.pdf

from PyQt5.QtCore import QThread
import pyvisa
import time

class driver_PTC10(QThread):

    def __init__(self, config):
        QThread.__init__(self)
        self.port = config['dev_port']
        self.retry = config['dev_retry']
        self.Tretry = config['dev_Tretry']
        self.Tdriver = config['dev_Tdriver']
        self.dev_type = config['dev_type']
        self.savefilename = config['dev_savefile']
        self.error = 0
        self.val = ['' for i in range(len(self.dev_type))]
        self.save = [False for i in range(len(self.dev_type))]
        self.valnames = ['' for i in range(len(self.dev_type))]
        self.runstate=False
        self.ready = 0
        value = True
        while value:
            if config['dev_interface'] == 'RS232':
                # just using COMX does not always work
                self.visaport = 'ASRL%s::INSTR' % self.port[3:]
            elif config['dev_interface'][0:4] == 'GPIB':
                self.visaport = '%s::%s::INSTR' % (config['dev_interface'],self.port)
            #elif config['dev_interface'] == 'ETH':
            
            try:
                rm = pyvisa.ResourceManager()
                self.inst = rm.open_resource(self.visaport)
                if config['dev_interface'] == 'RS232':
                    self.inst.baud_rate = config['dev_baudrate']
                    self.inst.write_termination = '\n'
                print(' ... PTC10 connected ...')
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
            out = self.inst.query("getOutputNames?").rstrip().split(",")
            self.valnames = [out[i-1] for i in self.dev_type]
            print(' ...',self.valnames)


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
                    out = self.inst.query("getOutput?")
                    readtime = time.time()
                    try:
                        self.values = out.rstrip().split(",")
                        self.val = [self.values[i-1] for i in self.dev_type]
                    except Exception:
                        self.val = ["" for i in range(len(self.dev_type))]

                    for deviceidx, tmpvalue in enumerate(self.save):
                        if(tmpvalue):
                            try:
                                with open(self.savefilename[deviceidx],"a") as file_a:
                                    file_a.write(str(readtime)+','+self.val[deviceidx]+'\n')
                                file_a.close
                            except Exception:
                                self.save[deviceidx] = False
                except Exception:
                    print('Connection to PTC10 lost.')
                    self.error = 1
            self.ready = 1
            time.sleep(self.Tdriver)
        self.ready = 0
