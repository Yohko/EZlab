# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

# adding new devices/drivers
# - create 'driver_...' class
# - update EZlab.init_UI and EZlab.update_controls

import sys
import numpy as np
import pyqtgraph as pg
import time
import signal
import os
#import math
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import QLabel, QSpinBox, QCheckBox, QComboBox
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLineEdit
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QFileDialog
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout
from PyQt5.QtCore import QTimer



if sys.platform == 'win32':
    os.system('cls') # for windows users
else:
    os.system('clear') # for unix users


# import GUI layout definitions
import config.config as EZconfig

# import devices drivers
import devices


f_debug = True

if f_debug:
    print('Available driver:',devices.available_driver)

if f_debug:
    print('Available Instruments:',devices.available_instr)

str_about = '© 2019-2021 Matthias H. Richter v2021124a\nMatthias.H.Richter@gmail.com\nhttps://github.com/Yohko/EZlab'



def signal_handler(sig, frame):
    QApplication.closeAllWindows()


class EZlab(QMainWindow):

    def __init__(self):
        super().__init__()
        self.config = dict()
        self.config['Instruments'] = EZconfig.Instruments
        self.check_config()
        self.title=EZconfig.EZlabtitle
        self.left=100
        self.top=100
        self.width=640
        self.height=200
        self.newfont = QFont("Times", 20, QFont.Bold)
        self.init_UI()


    def check_config(self):
        # simple config error check
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if f_debug:
                print(' ... testing configuration: '+devkey)

            if 'dev_enable' not in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['dev_enable'] = False

            if 'dev_driver' in self.config['Instruments'][devkey]:
                if self.config['Instruments'][devkey]['dev_driver'] not in devices.available_driver:
                    print('Driver Error in ' + devkey)
            else:
                print('Driver Error in ' + devkey)
                return

            if 'dev_interface' in self.config['Instruments'][devkey]:
                if self.config['Instruments'][devkey]['dev_interface'] == 'RS232':
                    if 'dev_baudrate' not in self.config['Instruments'][devkey]:
                        print('Baudrate Error in ' + devkey)
            else:
                print('Interface Error in ' + devkey)

            if 'dev_port' not in self.config['Instruments'][devkey]:
                print('Port rror in ' + devkey)

            if 'dev_label' not in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['dev_label'] = ('label%d' % devidx)
                print('Label Error in ' + devkey)

            if 'dev_savefile' not in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['dev_savefile'] = ('savefile%d.csv' % devidx)

            if 'dev_retry' not in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['dev_retry'] = False

            # time before attempting a new reconnect in sec
            if 'dev_Tretry' not in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['dev_Tretry'] = 10
            
            # sleep time for main driver loop in sec
            if 'dev_Tdriver' not in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['dev_Tdriver'] = 0.2


    def check_deverror(self, devidx, devkey):
        if (self.config['Instruments'][devkey]['GUI_thread'].error) and not (self.config['Instruments'][devkey]['GUI_disp'][devidx].text() == 'ERROR'):
            buf = ('-- ERROR -- dev: %s - label: %s' % (self.config['Instruments'][devkey]['dev_driver'],self.config['Instruments'][devkey]['dev_label']))
            self.statuslabel.setText(buf)
            if 'GUI_onoffcheck' in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['GUI_onoffcheck'][devidx].setEnabled(False)
            if 'GUI_savecheck' in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['GUI_savecheck'][devidx].setEnabled(False)
            if 'GUI_plotcheck' in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['GUI_plotcheck'][devidx].setEnabled(False)
            if 'GUI_mode' in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['GUI_mode'][devidx].setEnabled(False)
            if 'GUI_disp' in self.config['Instruments'][devkey]:
                self.config['Instruments'][devkey]['GUI_disp'][devidx].setText('ERROR')


    def init_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.MainLayout = QGridLayout() # the Main Gridlayout
        self.Mainwidget = QWidget()
        self.Mainwidget.setLayout(self.MainLayout)
        self.setCentralWidget(self.Mainwidget)
        
        maxrow = 1

        # dict to hold GUI layout
        self.config['GUI_groups'] = dict()
        
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                dev_driver = self.config['Instruments'][devkey]['dev_driver']
                if dev_driver in devices.available_driver:
                    # devkey defines groupname (and layout params)
                    groupname = devkey.split('::')[0]

                    ###############################################################
                    # Devices are grouped as specified by devkey (groupname) params
                    # add to GUI groups, check if group exists, else create it
                    ###############################################################
                    if not groupname in self.config['GUI_groups']:
                        if f_debug:
                            print(' ... create Group %s' % (groupname))
                        self.config['GUI_groups'][groupname] = dict()
                        self.config['GUI_groups'][groupname]['elements'] = -1
                        # create groupbox for this instrument group
                        if f_debug:
                            print(' ... create groupbox')
                        self.config['GUI_groups'][groupname]['Groupbox'] = QGroupBox(groupname)
                        # create a layout for this instrument group
                        if f_debug:
                            print(' ... create layout')
                        self.config['GUI_groups'][groupname]['layout'] = QGridLayout()
                        # add layout to instrument group groupbox
                        if f_debug:
                            print(' ... add layout to groupbox')
                        self.config['GUI_groups'][groupname]['Groupbox'].setLayout(self.config['GUI_groups'][groupname]['layout'])
                        # add instrument group groupbox to global layout
                        self.MainLayout.addWidget(
                                                    self.config['GUI_groups'][groupname]['Groupbox'], 
                                                    int(devkey.split('::')[1]), 
                                                    int(devkey.split('::')[2]),
                                                    int(devkey.split('::')[3]),
                                                    int(devkey.split('::')[4])
                                                    )
                        if maxrow <= (int(devkey.split('::')[1])+int(devkey.split('::')[3])-1):
                            maxrow = (int(devkey.split('::')[1])+int(devkey.split('::')[3]))
                    else:
                        if f_debug:
                            print(' ... group %s exists' % (groupname))


                    ###############################################################
                    # Instrument specific GUI elements etc
                    ###############################################################

                    ###############################################################
                    # K2100
                    ###############################################################
                    if dev_driver == 'K2100':
                        if f_debug:
                            print(' ... adding K2100 device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_K2100.driver_K2100(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')}
                        self.config['Instruments'][devkey]['GUI_label'] = {0:QLabel(('%s:') % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'] = {0:QCheckBox("save %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'][0].toggled.connect(self.clicked_save)
                        self.config['Instruments'][devkey]['GUI_plotcheck'] = {0:QPushButton("plot %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_plotcheck'][0].clicked.connect(self.clicked_plot)
                        self.config['Instruments'][devkey]['GUI_mode'] = {0:QComboBox()}
                        for mode in self.config['Instruments'][devkey]['GUI_thread'].modes: 
                            self.config['Instruments'][devkey]['GUI_mode'][0].addItem(mode)
                        self.config['Instruments'][devkey]['GUI_mode'][0].setCurrentIndex(int(self.config['Instruments'][devkey]['GUI_thread'].modes.index(
                            self.config['Instruments'][devkey]['dev_type']
                            )))
                        self.config['Instruments'][devkey]['GUI_mode'][0].currentIndexChanged.connect(self.switch_mode)
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_label'][0], self.config['GUI_groups'][groupname]['elements'], 0)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_disp'][0], self.config['GUI_groups'][groupname]['elements'], 1)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_savecheck'][0], self.config['GUI_groups'][groupname]['elements'], 2)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_plotcheck'][0], self.config['GUI_groups'][groupname]['elements'], 3)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_mode'][0], self.config['GUI_groups'][groupname]['elements'], 4)

                    ###############################################################
                    # K2000
                    ###############################################################
                    elif dev_driver == 'K2000':
                        if f_debug:
                            print(' ... adding K2000 device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_K2000.driver_K2000(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')}
                        self.config['Instruments'][devkey]['GUI_label'] = {0:QLabel(('%s:') % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'] = {0:QCheckBox("save %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'][0].toggled.connect(self.clicked_save)
                        self.config['Instruments'][devkey]['GUI_plotcheck'] = {0:QPushButton("plot %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_plotcheck'][0].clicked.connect(self.clicked_plot)
                        self.config['Instruments'][devkey]['GUI_mode'] = {0:QComboBox()}
                        for mode in self.config['Instruments'][devkey]['GUI_thread'].modes: 
                            self.config['Instruments'][devkey]['GUI_mode'][0].addItem(mode)
                        self.config['Instruments'][devkey]['GUI_mode'][0].setCurrentIndex(int(self.config['Instruments'][devkey]['GUI_thread'].modes.index(
                            self.config['Instruments'][devkey]['dev_type']
                            )))
                        self.config['Instruments'][devkey]['GUI_mode'][0].currentIndexChanged.connect(self.switch_mode)                        
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_label'][0], self.config['GUI_groups'][groupname]['elements'], 0)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_disp'][0], self.config['GUI_groups'][groupname]['elements'], 1)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_savecheck'][0], self.config['GUI_groups'][groupname]['elements'], 2)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_plotcheck'][0], self.config['GUI_groups'][groupname]['elements'], 3)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_mode'][0], self.config['GUI_groups'][groupname]['elements'], 4)

                    ###############################################################
                    # K2182A
                    ###############################################################
                    elif dev_driver == 'K2182A':
                        if f_debug:
                            print(' ... adding K2182A device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_K2182A.driver_K2182A(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')}
                        self.config['Instruments'][devkey]['GUI_label'] = {0:QLabel(('%s:') % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'] = {0:QCheckBox("save %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'][0].toggled.connect(self.clicked_save)
                        self.config['Instruments'][devkey]['GUI_plotcheck'] = {0:QPushButton("plot %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_plotcheck'][0].clicked.connect(self.clicked_plot)
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_label'][0], self.config['GUI_groups'][groupname]['elements'], 0)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_disp'][0], self.config['GUI_groups'][groupname]['elements'], 1)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_savecheck'][0], self.config['GUI_groups'][groupname]['elements'], 2)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_plotcheck'][0], self.config['GUI_groups'][groupname]['elements'], 3)

                    ###############################################################
                    # K2400
                    ###############################################################
                    elif dev_driver == 'K2400':
                        if f_debug:
                            print(' ... adding K2400 device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_K2400.driver_K2400(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')}
                        self.config['Instruments'][devkey]['GUI_label'] = {0:QLabel(('%s:') % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'] = {0:QCheckBox("save %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'][0].toggled.connect(self.clicked_save)
                        self.config['Instruments'][devkey]['GUI_onoffcheck'] = {0:QCheckBox("turn on %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_onoffcheck'][0].toggled.connect(self.clicked_onoff)
                        self.config['Instruments'][devkey]['GUI_plotcheck'] = {0:QPushButton("plot %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_plotcheck'][0].clicked.connect(self.clicked_plot)
                        self.config['Instruments'][devkey]['GUI_mode'] = {0:QComboBox()}
                        for mode in self.config['Instruments'][devkey]['GUI_thread'].modes:
                            self.config['Instruments'][devkey]['GUI_mode'][0].addItem(mode)
                        self.config['Instruments'][devkey]['GUI_mode'][0].setCurrentIndex(int(self.config['Instruments'][devkey]['GUI_thread'].modes.index(
                            self.config['Instruments'][devkey]['dev_type']
                            )))
                        self.config['Instruments'][devkey]['GUI_mode'][0].currentIndexChanged.connect(self.switch_mode)
                        self.config['Instruments'][devkey]['GUI_setP_edit']={0:QLineEdit()}
                        self.config['Instruments'][devkey]['GUI_setP_edit'][0].setValidator(QDoubleValidator(-5.00,+5.00,9))
                        self.config['Instruments'][devkey]['GUI_setP_edit'][0].setText('0.0')
                        # does not work
                        #self.config['Instruments'][devkey]['GUI_setP_edit'][0].editingFinished.connect(self.changed_setP)
                        # does not work
                        #self.config['Instruments'][devkey]['GUI_setP_edit'][0].returnPressed.connect(self.changed_setP)
                        self.config['Instruments'][devkey]['GUI_setP_edit'][0].textEdited.connect(self.changed_setP)
                        self.config['Instruments'][devkey]['GUI_compl_edit']={0:QLineEdit()}
                        self.config['Instruments'][devkey]['GUI_compl_edit'][0].setValidator(QDoubleValidator(0.00,42,9))
                        self.config['Instruments'][devkey]['GUI_compl_edit'][0].setText(str(self.config['Instruments'][devkey]['dev_compliance']))
                        # does not work
                        #self.config['Instruments'][devkey]['GUI_compl_edit'][0].editingFinished.connect(self.changed_compl)
                        # does not work
                        #self.config['Instruments'][devkey]['GUI_compl_edit'][0].returnPressed.connect(self.changed_compl)
                        self.config['Instruments'][devkey]['GUI_compl_edit'][0].textEdited.connect(self.changed_compl)
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_label'][0], self.config['GUI_groups'][groupname]['elements'], 0)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_disp'][0], self.config['GUI_groups'][groupname]['elements'], 1)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_savecheck'][0], self.config['GUI_groups'][groupname]['elements'], 2)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_plotcheck'][0], self.config['GUI_groups'][groupname]['elements'], 3)
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_setP_edit'][0], self.config['GUI_groups'][groupname]['elements'], 1)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_mode'][0], self.config['GUI_groups'][groupname]['elements'], 2)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_onoffcheck'][0], self.config['GUI_groups'][groupname]['elements'], 3)
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(QLabel('Compliance'), self.config['GUI_groups'][groupname]['elements'], 1)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_compl_edit'][0], self.config['GUI_groups'][groupname]['elements'], 2)

                    ###############################################################
                    # Newport69931
                    ###############################################################
                    elif dev_driver == 'Newport69931':
                        if f_debug:
                            print(' ... adding Newport69931 device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_Newport69931.driver_Newport69931(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')} # only for error checking
                        self.config['Instruments'][devkey]['GUI_onoffcheck'] = {0:QCheckBox("turn on %s" % self.config['Instruments'][devkey]['dev_label'])}
                        if self.config['Instruments'][devkey]['GUI_thread'].state:
                            self.config['Instruments'][devkey]['GUI_onoffcheck'][0].toggle()
                        self.config['Instruments'][devkey]['GUI_onoffcheck'][0].toggled.connect(self.clicked_onoff)
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_onoffcheck'][0], self.config['GUI_groups'][groupname]['elements'], 0)

                    ###############################################################
                    # Newport68945
                    ###############################################################
                    elif dev_driver == 'Newport68945':
                        if f_debug:
                            print(' ... adding Newport69931 device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_Newport68945.driver_Newport68945(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')} # only for error checking
                        self.config['Instruments'][devkey]['GUI_onoffcheck'] = {0:QCheckBox("turn on %s" % self.config['Instruments'][devkey]['dev_label'])}
                        if self.config['Instruments'][devkey]['GUI_thread'].state:
                            self.config['Instruments'][devkey]['GUI_onoffcheck'][0].toggle()
                        self.config['Instruments'][devkey]['GUI_onoffcheck'][0].toggled.connect(self.clicked_onoff)
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_onoffcheck'][0], self.config['GUI_groups'][groupname]['elements'], 0)

                    ###############################################################
                    # LambdaSC
                    ###############################################################
                    elif dev_driver == 'LambdaSC':
                        if f_debug:
                            print(' ... adding LambdaSC device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_LambdaSC.driver_LambdaSC(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')} # only for error checking
                        self.config['Instruments'][devkey]['GUI_onoffcheck'] = {0:QCheckBox("turn on %s" % self.config['Instruments'][devkey]['dev_label'])}
                        if self.config['Instruments'][devkey]['GUI_thread'].state:
                            self.config['Instruments'][devkey]['GUI_onoffcheck'][0].toggle()
                        self.config['Instruments'][devkey]['GUI_onoffcheck'][0].toggled.connect(self.clicked_onoff)
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_onoffcheck'][0], self.config['GUI_groups'][groupname]['elements'], 0)

                    ###############################################################
                    # RHUSB
                    ###############################################################
                    elif dev_driver == 'RHUSB':
                        if f_debug:
                            print(' ... adding RHUSB device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_RHUSB.driver_RHUSB(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')}
                        self.config['Instruments'][devkey]['GUI_label'] = {0:QLabel(('%s:') % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'] = {0:QCheckBox("save %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'][0].toggled.connect(self.clicked_save)
                        self.config['Instruments'][devkey]['GUI_plotcheck'] = {0:QPushButton("plot %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_plotcheck'][0].clicked.connect(self.clicked_plot)
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_label'][0], self.config['GUI_groups'][groupname]['elements'], 0)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_disp'][0], self.config['GUI_groups'][groupname]['elements'], 1)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_savecheck'][0], self.config['GUI_groups'][groupname]['elements'], 2)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_plotcheck'][0], self.config['GUI_groups'][groupname]['elements'], 3)

                    ###############################################################
                    # SPERSCI80005
                    ###############################################################
                    elif dev_driver == 'SPERSCI80005':
                        if f_debug:
                            print(' ... adding SPERSCI80005 device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_SPERSCI80005.driver_SPERSCI80005(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # create GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = {0:QLabel('')}
                        self.config['Instruments'][devkey]['GUI_label'] = {0:QLabel(('%s:') % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'] = {0:QCheckBox("save %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_savecheck'][0].toggled.connect(self.clicked_save)
                        self.config['Instruments'][devkey]['GUI_plotcheck'] = {0:QPushButton("plot %s" % self.config['Instruments'][devkey]['dev_label'])}
                        self.config['Instruments'][devkey]['GUI_plotcheck'][0].clicked.connect(self.clicked_plot)
                        # add GUI elements to group
                        self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_label'][0], self.config['GUI_groups'][groupname]['elements'], 0)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_disp'][0], self.config['GUI_groups'][groupname]['elements'], 1)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_savecheck'][0], self.config['GUI_groups'][groupname]['elements'], 2)
                        self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_plotcheck'][0], self.config['GUI_groups'][groupname]['elements'], 3)

                    ###############################################################
                    # PTC10
                    ###############################################################
                    elif dev_driver == 'PTC10':
                        if f_debug:
                            print(' ... adding PTC10 device ...')
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_PTC10.driver_PTC10(
                                self.config['Instruments'][devkey]
                                )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # add empty dicts for GUI elements
                        self.config['Instruments'][devkey]['GUI_disp'] = dict()
                        self.config['Instruments'][devkey]['GUI_label'] = dict()
                        self.config['Instruments'][devkey]['GUI_savecheck'] = dict()
                        self.config['Instruments'][devkey]['GUI_plotcheck'] = dict()
                        # loop through all selected outputs
                        for PTCidx in range(len(self.config['Instruments'][devkey]['dev_type'])):
                            # create GUI elements
                            self.config['Instruments'][devkey]['GUI_disp'][PTCidx] = QLabel('')
                            self.config['Instruments'][devkey]['GUI_label'][PTCidx] = QLabel(('%s:') % self.config['Instruments'][devkey]['dev_label'][PTCidx])
                            self.config['Instruments'][devkey]['GUI_savecheck'][PTCidx] = QCheckBox("save %s" % self.config['Instruments'][devkey]['dev_label'][PTCidx])
                            self.config['Instruments'][devkey]['GUI_savecheck'][PTCidx].toggled.connect(self.clicked_save)
                            self.config['Instruments'][devkey]['GUI_plotcheck'][PTCidx] = QPushButton("plot %s" % self.config['Instruments'][devkey]['dev_label'][PTCidx])
                            self.config['Instruments'][devkey]['GUI_plotcheck'][PTCidx].clicked.connect(self.clicked_plot)
                            # add GUI elements to group
                            self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1
                            self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_label'][PTCidx], self.config['GUI_groups'][groupname]['elements'], 0)
                            self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_disp'][PTCidx], self.config['GUI_groups'][groupname]['elements'], 1)
                            self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_savecheck'][PTCidx], self.config['GUI_groups'][groupname]['elements'], 3)
                            self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['Instruments'][devkey]['GUI_plotcheck'][PTCidx], self.config['GUI_groups'][groupname]['elements'], 4)

                    ###############################################################
                    # Alicat
                    ###############################################################
                    elif dev_driver == 'Alicat':
                        if f_debug:
                            print(' ... adding Alicat device ...')
 
                        # create the device thread
                        self.config['Instruments'][devkey]['GUI_thread'] = devices.dev_Alicat.driver_Alicat(
                            self.config['Instruments'][devkey]
                            )
                        # start device thread
                        self.config['Instruments'][devkey]['GUI_thread'].start()
                        # wait for Thread to finish device initialization
                        while(self.config['Instruments'][devkey]['GUI_thread'].ready !=1):
                            time.sleep(1)
                        # add empty dicts during first call
                        self.config['Instruments'][devkey]['GUI_flow_edit'] = dict()
                        self.config['Instruments'][devkey]['GUI_disp'] = dict()
                        self.config['Instruments'][devkey]['GUI_savecheck'] = dict()
                        self.config['Instruments'][devkey]['GUI_plotcheck'] = dict()
                        self.config['Instruments'][devkey]['GUI_setP'] = dict()
                        self.config['Instruments'][devkey]['GUI_setG'] = dict()
                        self.config['Instruments'][devkey]['GUI_gas_edit'] = dict()
                        self.config['Instruments'][devkey]['GUI_label'] = dict()
                        self.config['Instruments'][devkey]['GUI_unit'] = dict()
                        # loop through all devices on the bus
                        for Alicatidx in range(len(self.config['Instruments'][devkey]['dev_id'])):
                            if not 'elements_Alicat' in self.config['GUI_groups'][groupname]:
                                self.config['GUI_groups'][groupname]['elements_Alicat'] = -1;
                                self.config['GUI_groups'][groupname]['elements'] = self.config['GUI_groups'][groupname]['elements'] + 1;

                            self.config['GUI_groups'][groupname]['elements_Alicat'] = self.config['GUI_groups'][groupname]['elements_Alicat'] + 1;
                            tmpnum = self.config['GUI_groups'][groupname]['elements_Alicat']
                            self.config['Instruments'][devkey]['GUI_flow_edit'][Alicatidx]=QSpinBox()
                            self.config['Instruments'][devkey]['GUI_flow_edit'][Alicatidx].setRange(0,500)
                            self.config['Instruments'][devkey]['GUI_disp'][Alicatidx]=QLabel('')
                            self.config['Instruments'][devkey]['GUI_savecheck'][Alicatidx]=QCheckBox("save %s" % self.config['Instruments'][devkey]['dev_label'][Alicatidx])
                            self.config['Instruments'][devkey]['GUI_savecheck'][Alicatidx].toggled.connect(self.clicked_save)
                            self.config['Instruments'][devkey]['GUI_plotcheck'][Alicatidx]=QPushButton("plot %s" % self.config['Instruments'][devkey]['dev_label'][Alicatidx])
                            self.config['Instruments'][devkey]['GUI_plotcheck'][Alicatidx].clicked.connect(self.clicked_plot)
                            self.config['Instruments'][devkey]['GUI_setP'][Alicatidx]=0
                            self.config['Instruments'][devkey]['GUI_setG'][Alicatidx]=0
                            self.config['Instruments'][devkey]['GUI_gas_edit'][Alicatidx]=QComboBox()
                            self.config['Instruments'][devkey]['GUI_label'][Alicatidx]=QLabel('%s:' % self.config['Instruments'][devkey]['dev_label'][Alicatidx])
                            # get initial device reading to populate initial GUI elements
                            # if this is not done, the device will be reset to a standard config 
                            # (to whatever the default value of the GUI elements is)
                            # and not keep its current set values (setpopint and gas type)
                            for gas in self.config['Instruments'][devkey]['GUI_thread'].gases: 
                                self.config['Instruments'][devkey]['GUI_gas_edit'][Alicatidx].addItem(gas)
                            self.config['Instruments'][devkey]['GUI_flow_edit'][Alicatidx].setValue(int(self.config['Instruments'][devkey]['GUI_thread'].setP[Alicatidx]*10))
                            self.config['Instruments'][devkey]['GUI_gas_edit'][Alicatidx].setCurrentIndex(int(self.config['Instruments'][devkey]['GUI_thread'].setG[Alicatidx]))
                            if self.config['Instruments'][devkey]['dev_type'][Alicatidx] == 1: # flow controller
                                self.config['Instruments'][devkey]['GUI_unit'][Alicatidx]=QLabel('sccm*10')
                            elif self.config['Instruments'][devkey]['dev_type'][Alicatidx] == 2: # flow meter
                                self.config['Instruments'][devkey]['GUI_unit'][Alicatidx]=QLabel('sccm*10')
                            # check if this is the first Alicat device and if create all subgroups
                            if self.config['GUI_groups'][groupname]['elements_Alicat'] == 0:
                                # setpoint group
                                self.config['GUI_groups'][groupname]['Groupbox_setpoint'] = QGroupBox('set point')
                                self.config['GUI_groups'][groupname]['layout_setpoint'] = QGridLayout()
                                self.config['GUI_groups'][groupname]['Groupbox_setpoint'].setLayout(self.config['GUI_groups'][groupname]['layout_setpoint'])
                                # setpoint group
                                self.config['GUI_groups'][groupname]['Groupbox_gastype'] = QGroupBox('gas type')
                                self.config['GUI_groups'][groupname]['layout_gastype'] = QGridLayout()
                                self.config['GUI_groups'][groupname]['Groupbox_gastype'].setLayout(self.config['GUI_groups'][groupname]['layout_gastype'])
                                # flowrate group
                                self.config['GUI_groups'][groupname]['Groupbox_flowrate'] = QGroupBox('flow rate')
                                self.config['GUI_groups'][groupname]['layout_flowrate'] = QGridLayout()
                                self.config['GUI_groups'][groupname]['Groupbox_flowrate'].setLayout(self.config['GUI_groups'][groupname]['layout_flowrate'])
                                # add groups to main device groupbox
                                self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['GUI_groups'][groupname]['Groupbox_setpoint'],self.config['GUI_groups'][groupname]['elements'],0)       
                                self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['GUI_groups'][groupname]['Groupbox_gastype'],self.config['GUI_groups'][groupname]['elements'],1)
                                self.config['GUI_groups'][groupname]['layout'].addWidget(self.config['GUI_groups'][groupname]['Groupbox_flowrate'],self.config['GUI_groups'][groupname]['elements'],2)
                            # now add all Alicat speficic GUI elements
                            # for setpoint
                            if self.config['Instruments'][devkey]['dev_type'][Alicatidx] == 1: # flow controller
                                self.config['GUI_groups'][groupname]['layout_setpoint'].addWidget(self.config['Instruments'][devkey]['GUI_label'][Alicatidx], tmpnum, 0)
                                self.config['GUI_groups'][groupname]['layout_setpoint'].addWidget(self.config['Instruments'][devkey]['GUI_flow_edit'][Alicatidx], tmpnum, 1)
                                self.config['GUI_groups'][groupname]['layout_setpoint'].addWidget(self.config['Instruments'][devkey]['GUI_unit'][Alicatidx], tmpnum, 2)
                            if self.config['Instruments'][devkey]['dev_type'][Alicatidx] == 2: # flow meter
                                self.config['GUI_groups'][groupname]['layout_setpoint'].addWidget(self.config['Instruments'][devkey]['GUI_label'][Alicatidx], tmpnum, 0)
                                self.config['GUI_groups'][groupname]['layout_setpoint'].addWidget(self.config['Instruments'][devkey]['GUI_flow_edit'][Alicatidx], tmpnum, 1)
                                self.config['GUI_groups'][groupname]['layout_setpoint'].addWidget(self.config['Instruments'][devkey]['GUI_unit'][Alicatidx], tmpnum, 2)
                                self.config['Instruments'][devkey]['GUI_flow_edit'][Alicatidx].setEnabled(False)
                            # for gas type
                            self.config['GUI_groups'][groupname]['layout_gastype'].addWidget(self.config['Instruments'][devkey]['GUI_gas_edit'][Alicatidx], tmpnum, 0)
                            # for readout
                            self.config['GUI_groups'][groupname]['layout_flowrate'].addWidget(self.config['Instruments'][devkey]['GUI_disp'][Alicatidx], tmpnum, 0)
                            self.config['GUI_groups'][groupname]['layout_flowrate'].addWidget(self.config['Instruments'][devkey]['GUI_savecheck'][Alicatidx], tmpnum, 1)
                            self.config['GUI_groups'][groupname]['layout_flowrate'].addWidget(self.config['Instruments'][devkey]['GUI_plotcheck'][Alicatidx], tmpnum, 2)



        # add about section
        self.MainLayout.addWidget(QLabel(str_about), maxrow, 0, 1, 2)
        self.statuslabel = QLabel('no Error')
        self.MainLayout.addWidget(self.statuslabel, maxrow, 2, 1, 1)

        timer = QTimer(self)
        timer.timeout.connect(self.update_controls)
        timer.start(500)
        self.show()


    def clicked_save(self):
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                if 'GUI_savecheck' in self.config['Instruments'][devkey]:
                    btn = self.config['Instruments'][devkey]['GUI_savecheck']
                    for subdevidx, subbtn in btn.items():
                        if subbtn == self.sender():
                            if subbtn.isChecked() == True:
                                print(' ... '+subbtn.text()+" is selected")
                                filename = self.show_savedialog(self.config['Instruments'][devkey]['GUI_thread'].savefilename[subdevidx])
                                if filename == '':
                                    self.config['Instruments'][devkey]['GUI_thread'].save[subdevidx] = False
                                    subbtn.toggle()
                                else:
                                    self.config['Instruments'][devkey]['GUI_thread'].savefilename[subdevidx] = filename
                                    self.config['Instruments'][devkey]['GUI_thread'].save[subdevidx] = True
                                    if isinstance(self.config['Instruments'][devkey]['dev_label'],list):
                                        print('Saving '+self.config['Instruments'][devkey]['dev_label'][subdevidx] +' to ' + filename)
                                    else:
                                        print('Saving '+self.config['Instruments'][devkey]['dev_label'] +' to ' + filename)                                            
                            else:
                                self.config['Instruments'][devkey]['GUI_thread'].save[subdevidx] = False
                                print(' ... '+subbtn.text()+' is deselected')


    def clicked_onoff(self):
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                if 'GUI_onoffcheck' in self.config['Instruments'][devkey]:
                    btn = self.config['Instruments'][devkey]['GUI_onoffcheck']
                    for subdevidx, subbtn in btn.items():
                        if subbtn == self.sender():
                            if subbtn.isChecked() == True:
                                self.config['Instruments'][devkey]['GUI_thread'].newstate[subdevidx] = True
                            else:
                                self.config['Instruments'][devkey]['GUI_thread'].newstate[subdevidx] = False
                            return


    def clicked_plot(self):
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                if 'GUI_plotcheck' in self.config['Instruments'][devkey]:
                    btn = self.config['Instruments'][devkey]['GUI_plotcheck']
                    for subdevidx, subbtn in btn.items():
                        if subbtn == self.sender():
                            if 'GUI_plotwindow' not in self.config['Instruments'][devkey]:
                                self.config['Instruments'][devkey]['GUI_plotwindow'] = dict()
                            if subdevidx not in self.config['Instruments'][devkey]['GUI_plotwindow']:
                                if isinstance(self.config['Instruments'][devkey]['dev_label'],list):
                                    self.config['Instruments'][devkey]['GUI_plotwindow'][subdevidx]=plot_widget(self.config['Instruments'][devkey]['dev_label'][subdevidx]+' vs. time plot',self.config['Instruments'][devkey]['dev_label'][subdevidx])
                                else:
                                    self.config['Instruments'][devkey]['GUI_plotwindow'][subdevidx]=plot_widget(self.config['Instruments'][devkey]['dev_label']+' vs. time plot',self.config['Instruments'][devkey]['dev_label'])
                                self.config['Instruments'][devkey]['GUI_plotwindow'][subdevidx].show()
                            else:
                                self.config['Instruments'][devkey]['GUI_plotwindow'][subdevidx].show()
                            return


    def show_savedialog(self, default_name):
        selected_filter = "data file (*.csv)"
        filename = QFileDialog.getSaveFileName(self,"select file to save", default_name,selected_filter)
        return filename[0]


    def switch_mode(self,i):
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                if 'GUI_mode' in self.config['Instruments'][devkey]:
                    btn = self.config['Instruments'][devkey]['GUI_mode']
                    for subdevidx, subbtn in btn.items():
                        if subbtn == self.sender():
                            self.config['Instruments'][devkey]['GUI_thread'].newmode[subdevidx] = subbtn.itemText(i)
                            return


    def changed_setP(self, text):
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                if 'GUI_setP_edit' in self.config['Instruments'][devkey]:
                    btn = self.config['Instruments'][devkey]['GUI_setP_edit']
                    for subdevidx, subbtn in btn.items():
                        if subbtn == self.sender():
                            if text == '':
                                text = '0.0'
                            self.config['Instruments'][devkey]['GUI_thread'].newsetP[0]=float(text)
                            return


    def changed_compl(self, text):
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                if 'GUI_compl_edit' in self.config['Instruments'][devkey]:
                    btn = self.config['Instruments'][devkey]['GUI_compl_edit']
                    for subdevidx, subbtn in btn.items():
                        if subbtn == self.sender():
                            if text == '':
                                text = '0.0'
                            self.config['Instruments'][devkey]['GUI_thread'].newcompliance[0]=float(text)
                            return


    def update_controls(self):
        # this is the main update function which gets call every few ms
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                dev_driver = self.config['Instruments'][devkey]['dev_driver']
                if dev_driver in devices.available_driver:


                    if isinstance(self.config['Instruments'][devkey]['dev_label'],list):
                        subdevcount = len(self.config['Instruments'][devkey]['dev_label'])
                    else:
                        subdevcount = 1

                    for subdevidx in range(subdevcount):
                        # check for errors
                        self.check_deverror(subdevidx, devkey)

                        if self.config['Instruments'][devkey]['GUI_thread'].error == 0:
                            # update display
                            if 'GUI_disp' in self.config['Instruments'][devkey]:
                                self.config['Instruments'][devkey]['GUI_disp'][subdevidx].setText(
                                    self.config['Instruments'][devkey]['GUI_thread'].dispbuf[subdevidx])
                            # update plot
                            if 'GUI_plotwindow' in self.config['Instruments'][devkey]:
                                if subdevidx in self.config['Instruments'][devkey]['GUI_plotwindow']:
                                    self.config['Instruments'][devkey]['GUI_plotwindow'][subdevidx].update_plot(
                                        time.time(), 
                                        self.config['Instruments'][devkey]['GUI_thread'].plotval[subdevidx])

                            ###################################################
                            # Instrument specific GUI elements etc
                            ###################################################

                            ###################################################
                            # Alicat
                            ###################################################
                            if dev_driver == 'Alicat':
                                # check device set points against set points of GUI elements
                                # and update device set points accordingly
                                # get current device set point:
                                self.config['Instruments'][devkey]['GUI_setP'][subdevidx] = self.config['Instruments'][devkey]['GUI_thread'].setP[subdevidx]
                                self.config['Instruments'][devkey]['GUI_setG'][subdevidx] = self.config['Instruments'][devkey]['GUI_thread'].setG[subdevidx]
                                # set controller set points
                                if self.config['Instruments'][devkey]['dev_type'][subdevidx] == 1: # flow controller
                                    if ((self.config['Instruments'][devkey]['GUI_flow_edit'][subdevidx].value()/10)!=self.config['Instruments'][devkey]['GUI_setP'][subdevidx]):
                                        self.config['Instruments'][devkey]['GUI_thread'].setPnew[subdevidx] = self.config['Instruments'][devkey]['GUI_flow_edit'][subdevidx].value()/10
                                # set gas types
                                if (self.config['Instruments'][devkey]['GUI_gas_edit'][subdevidx].currentIndex()!=self.config['Instruments'][devkey]['GUI_setG'][subdevidx]):
                                   self.config['Instruments'][devkey]['GUI_thread'].setGnew[subdevidx] = self.config['Instruments'][devkey]['GUI_gas_edit'][subdevidx].currentIndex()


    def closeEvent(self, event):
        for devidx, devkey in enumerate(list(self.config['Instruments'].keys())):
            if self.config['Instruments'][devkey]['dev_enable']:
                if f_debug:
                    print(' ... shutting down: '+devkey)

                # closing all plots
                if 'GUI_plotcheck' in self.config['Instruments'][devkey]:
                    btn = self.config['Instruments'][devkey]['GUI_plotcheck']
                    for subdevidx, subbtn in btn.items():
                        if 'GUI_plotwindow' in self.config['Instruments'][devkey]:
                            if subdevidx in self.config['Instruments'][devkey]['GUI_plotwindow']:
                                self.config['Instruments'][devkey]['GUI_plotwindow'][subdevidx].close()
                # stop thread
                self.config['Instruments'][devkey]['GUI_thread'].stop()


class plot_widget(QWidget):
    
    def __init__(self, mytitle, ylabel):
        super().__init__()
        self.title = mytitle
        self.ylabel = ylabel
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.graphWidget = pg.PlotWidget()
        self.setWindowTitle(self.title)
        self.setFixedWidth(400)
        self.setFixedHeight(200)
        self.points=1000 #number of data points
        self.X=[]
        self.Y=dict() 
        layout.addWidget(self.graphWidget)
    

    def update_plot(self, newx, newy):
        self.X = np.append(self.X, newx)
        for tmpid, tmpval in enumerate(newy):
            if tmpid in self.Y:
                self.Y[tmpid] = np.append(self.Y[tmpid], tmpval)
            else:
                self.Y[tmpid] = [tmpval]

            if len(self.X) > self.points:
                self.Y[tmpid] = np.delete(self.Y[tmpid],0)
                
        if len(self.X) > self.points:
            self.X = np.delete(self.X, 0)

        for plotid, plotkey in enumerate(newy):
            if plotid > 0:
                self.graphWidget.plot((self.X-self.X[len(self.X)-1])/3600,
                                      self.Y[plotid],clear=False,
                                      pen=pg.mkPen('b', width=2))
            else:
                self.graphWidget.plot((self.X-self.X[len(self.X)-1])/3600,
                                      self.Y[plotid],clear=True,
                                      pen=pg.mkPen('r', width=2))

        self.graphWidget.setLabel('left', self.ylabel)
        self.graphWidget.setLabel('bottom', 'time (h)')


if __name__=='__main__':
    signal.signal(signal.SIGINT, signal_handler)
    app=QApplication(sys.argv)
    ex=EZlab()
    sys.exit(app.exec_())
