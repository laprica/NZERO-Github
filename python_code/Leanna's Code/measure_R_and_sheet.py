import visa
import numpy as np
import time
import os.path
import sys
import keithley2400 as kt
import logging
from matplotlib import pyplot as plt

""" Script to measure resistance and to get sheet resistance from
    measuring a resistor on the characterization die from mask V6"""

""" Created by Leanna Pancoast 27 Feb 2017 """

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }


#### ******* VARIABLES TO SET *************
# change these to set address
# use rm.list_resources() in shell to see
#cont_keithley_addr = 'GPIB0::25::INSTR'
cont_keithley_addr = 'GPIB0::2::INSTR'

device_name = 'blah'

v_start = 5e-1
v_step = 0.5*1e-1
v_end = 9*1e-1

omega1 = 0
omega2 = 0

logs_folder_path = "C:\\Users\\MOLNAR_PH330_D1\\Desktop\\NZERO\\python_code\\logs\\"
now = time.strftime('%Y%m%d_%H%M%S')
# total log
fn = "{}resistance_{}_log.txt".format(logs_folder_path, device_name,now,)

# lets us talk to GPIB
rm = visa.ResourceManager()

# gives us an instrument to work with
inst_cont = rm.open_resource(cont_keithley_addr)

cont_kt = kt.KT2400(inst_cont)
print('starting measurement')

currs = []
res = []

def getSheetR(resistance):
    # resistance = (resitivity & length)/(thickness * width)
    # for devices (9/21/2017)
    # resitivity = Resistance * thickness/(# of square with equal w and L)
    thickness = 2.5e-4 #2 um
    numSquare1 = 85
    numSquareC1 = 12
    
    numSquare2 = 13
    numSquareC2 = 0

    numSquarePad = 2
    
    x = (resistance * thickness)/(numSquare1 + 0.56*numSquareC1 + numSquarePad)
    y = (resistance * thickness)/(numSquare2 + 0.56*numSquareC2 + numSquarePad)
    print 'omega1: {}'.format(x)
    print 'omega2: {}'.format(y)
    return x
    
    
def main():
    global cont_kt, v_start, v_step, v_end
    ##### ******* START MEASUREMENT INITIALIZATION *******
    print('starting initialization')
    ## Initialize
    # set keithley's to volt source mode
    cont_kt.set_mode('VOLT')

  
    ##### ******* STARTING MEASUREMENT ********
    raw_input('*Press enter to start test of {}\n'.format(device_name))
    cont_kt.beep(740,0.5)

    # read currents

    cont_kt.set_volt(v_start)
    cont_kt.read_curr()

    for v in np.arange(v_start,v_end,v_step):
        cont_kt.set_volt(v)
        x = cont_kt.read_curr()
        print 'curr:{}'.format(x)
        print 'res: {}'.format(v/x)
        currs.append(x)
        res.append(v/x)
    
    # beep to know test is done
    cont_kt.beep(523,0.5)

    cont_kt.set_volt(0)

    print 'average res: {:,}'.format(np.average(res))

    omega = getSheetR(np.average(res))

    fig = plt.figure()
    #ax = fig.add_subplot(111)

    plt.plot(np.arange(v_start,v_end,v_step),currs)
    plt.title('Released Ultrasil (SOI9-1-M1R-0) B0ToChuck')
    #plt.text(1.7,1.9e-8,'Resistance (ohm): {:.2e}\nResistivity (ohm-cm): {:.2e}'.format(np.average(res),omega),fontdict=font)

    plt.show()

# so that when ctrl+c, files will still close and voltage resets

try:
    main()
except KeyboardInterrupt:
    bias_kt.set_volt(0)
    cont_kt.set_volt(0)
    print('closed with ctrl+c')
    log.info('closed with ctrl+c')
    sys.exit(0)
