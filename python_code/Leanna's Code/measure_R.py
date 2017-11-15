import visa
import numpy as np
import time
import os.path
import sys
import keithley2400 as kt
import logging
from matplotlib import pyplot as plt

""" Script to measure resistance """

""" Created by Leanna Pancoast 27 Feb 2017 """


#### ******* VARIABLES TO SET *************
# change these to set address
# use rm.list_resources() in shell to see
cont_keithley_addr = 'GPIB0::25::INSTR'
#cont_keithley_addr = 'GPIB0::2::INSTR'

v_start = 5
v_step = 0.5
v_end = 12



logs_folder_path = "C:\\Users\\MOLNAR_PH330_D1\\Desktop\\NZERO\\python_code\\logs\\"
now = time.strftime('%Y%m%d_%H%M%S')
# total log
fn = "resistance_{}_log.txt".format(logs_folder_path,now,)


## SETUP KEITHLEY

# lets us talk to GPIB
rm = visa.ResourceManager()

# gives us an instrument to work with
inst_cont = rm.open_resource(cont_keithley_addr)

cont_kt = kt.KT2400(inst_cont)

## END SETUP KEITHLEY

print('starting measurement')

currs = []
res = []
    
def main():
    global cont_kt, v_start, v_step, v_end
    ##### ******* START MEASUREMENT INITIALIZATION *******
    print('starting initialization')
    ## Initialize
    # set keithley's to volt source mode
    cont_kt.set_mode('VOLT')

  
    ##### ******* STARTING MEASUREMENT ********
    raw_input('*Press enter to start test\n')
    cont_kt.beep(740,0.5)

    # read currents

    cont_kt.set_volt(v_start)
    cont_kt.read_curr()

    for v in np.arange(v_start,v_end,v_step):
        cont_kt.set_volt(v)
        x = cont_kt.read_curr()
        print 'curr:{}'.format(x)
        print 'res: {:,}'.format(v/x)
        currs.append(x*1e-6)
        res.append(v/x)
    
    # beep to know test is done
    cont_kt.beep(523,0.5)

    cont_kt.set_volt(0)

    print '{:,}'.format(np.average(res))

    plt.figure()

    plt.plot(np.arange(v_start,v_end,v_step),currs)

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
