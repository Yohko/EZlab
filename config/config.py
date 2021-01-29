# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019-2021 Matthias H. Richter

EZlabtitle = 'Gas flow control widget'

# Definitions of active instruments
# Set enable to false if not in use
Instruments = dict()

Instruments['Gas Flow::0::0::1::3::Stanford'] = dict(
             dev_enable=False,
             dev_driver='Alicat',
             dev_interface='RS232',
             dev_port='COM1',
             dev_baudrate=9600,
             dev_id=['A','B'],
             dev_type=[1,2],
             dev_label=['In','Out'],
             dev_savefile=['In_gasflow.csv','Out_gasflow.csv'],
             dev_retry = True,
             dev_Tretry = 5
             )

Instruments['Multimeter::1::0::1::2::dev1'] = dict(
             dev_enable=True,
             dev_driver='K2100',
             dev_interface='USB',
             dev_port='USB0::0x05E6::0x2100::1373846::INSTR',
             dev_id='KEITHLEY INSTRUMENTS INC.,MODEL 2100,1,01.08-01-01',
             dev_type='V DC',
             dev_label='Cell',
             dev_savefile='CellVoltage.csv',
             dev_retry = True,
             dev_Tretry = 5
             )

Instruments['Multimeter::1::0::1::2::dev2'] = dict(
             dev_enable=True,
             dev_driver='K2100',
             dev_interface='USB',
             dev_port='USB0::0x05E6::0x2100::1420416::INSTR',
             dev_id='KEITHLEY INSTRUMENTS INC.,MODEL 2100,1,01.08-01-01',
             dev_type='V DC',
             dev_label='CE',
             dev_savefile='CEvsREF.csv',
             dev_retry = True,
             dev_Tretry = 5
         )

Instruments['Multimeter::1::0::1::2::dev3'] = dict(
             dev_enable=True,
             dev_driver='K2100',
             dev_interface='USB',
             dev_port='USB0::0x05E6::0x2100::1420629::INSTR',
             dev_id='KEITHLEY INSTRUMENTS INC.,MODEL 2100,1,01.08-01-01',
             dev_type='V DC',
             dev_label='WE',
             dev_savefile='WEvsREF.csv',
             dev_retry = True,
             dev_Tretry = 5
         )

Instruments['Multimeter::1::0::1::2::dev4'] = dict(
             dev_enable=True,
             dev_driver='K2000',
             dev_interface='RS232',
             dev_port='COM14',
             dev_baudrate=9600,
             dev_id='KEITHLEY INSTRUMENTS INC.,MODEL 2000',
             dev_type='V DC',
             dev_label='Misc',
             dev_savefile='MiscVoltage.csv',
             dev_retry = True,
             dev_Tretry = 5
         )

Instruments['Multimeter::1::0::1::2::dev5'] = dict(
             dev_enable=True,
             dev_driver='K2182A',
             dev_interface='RS232',
             dev_port='COM15',
             dev_baudrate=9600,
             dev_id='KEITHLEY INSTRUMENTS INC.,MODEL 2182A',
             dev_type='V',
             dev_label='Misc2',
             dev_savefile='MiscVoltage.csv',
             dev_retry = False,
             dev_Tretry = 5
         )

Instruments['Multimeter::1::0::1::2::dev6'] = dict(
             dev_enable=False,
             dev_driver='K2400',
             dev_interface='RS232',
             dev_port='COM5',
             dev_baudrate=9600,
             dev_id='KEITHLEY INSTRUMENTS INC.,MODEL 2440',
             dev_type='V',
             dev_compliance =1,
             dev_setP = 0,
             dev_label='Power',
             dev_savefile='Source.csv',
             dev_retry = True,
             dev_Tretry = 5
         )

Instruments['Gas Flow::0::0::1::3::dev1'] = dict(
             dev_enable=True,
             dev_driver='Alicat',
             dev_interface='RS232',
             dev_port='COM10',
             dev_baudrate=9600,
             dev_id=['A'], # need [] because of multiple controllers on same port
             dev_type=[1], # Flow Controller
             dev_label=['A'],
             dev_savefile=['A_gasflow.csv']
         )

Instruments['Gas Flow::0::0::1::3::dev2'] = dict(
             dev_enable=True,
             dev_driver='Alicat',
             dev_interface='RS232',
             dev_port='COM12',
             dev_baudrate=9600,
             dev_id=['B'], # need [] because of multiple controllers on same port
             dev_type=[2], # Flow meter
             dev_label=['B'],
             dev_savefile=['B_gasflow.csv']
         )

Instruments['Lamp::1::2::1::1::dev1'] = dict(
             dev_enable=True,
             dev_driver='Newport69931',
             dev_interface='RS232',
             dev_port='COM9',
             dev_baudrate=9600,
             dev_label='Xenon lamp',
             dev_Tblock = 60*60, # time before the lamp status can be changed again
             dev_Tdriver = 1
         )

Instruments['Lamp::1::2::1::1::dev2'] = dict(
             dev_enable=True,
             dev_driver='Newport68945',
             dev_interface='RS232',
             dev_port='COM11',
             dev_baudrate=9600,
             dev_label='Shutter',
             dev_Tdriver = 1
         )

Instruments['Humidity::3::0::1::2::dev1'] = dict(
             dev_enable=True,
             dev_driver='RHUSB',
             dev_interface='RS232',
             dev_port='COM6',
             dev_baudrate=9600,
             dev_label='Humidity',
             dev_savefile='RHUSB.csv',
             dev_Tdriver = 1
         )

Instruments['Temperature::4::0::1::2::dev1'] = dict(
             dev_enable=True,
             dev_driver='PTC10',
             dev_interface='RS232',
             dev_port='COM13',
             dev_baudrate=9600,
             dev_label=['HEATER', 'RTD', 'TC1', 'TC2'],
             dev_units=['W', '°C', '°C', '°C'],
             dev_type=[1,2,3,4], # start with 1
             dev_savefile=['HEATER.csv', 'RTD.csv', 'TC1.csv', 'TC2.csv'],
             dev_Tdriver = 1
         )

Instruments['Temperature::4::0::1::2::dev2'] = dict(
             dev_enable=False,
             dev_driver='SPERSCI80005',
             dev_interface='RS232',
             dev_port='COM4',
             dev_baudrate=9600,
             dev_type=1,
             dev_id='302',
             dev_label='Temp',
             dev_savefile='Temp.csv',
             dev_Tdriver = 1
         )
