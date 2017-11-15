import visa
import numpy as np
import time
import os.path
import sys
import keithley2400 as kt
import logging
from matplotlib import pyplot as plt

""" Script to do contact pulse hysteresis test of NZERO NEMS Switch """
""" This is modified to be able to test a single switch on a chip"""

""" Created by Leanna Pancoast 17 Oct 2017 """


#### ******* VARIABLES TO SET *************
# change these to set address
# use rm.list_resources() in shell to see
bias_keithley_addr = 'GPIB0::25::INSTR'
cont_keithley_addr = 'GPIB0::2::INSTR'



device_name = 'SOI8-10-M1R-7-E2'




# starting bias voltage
bias_start = 0
# bias step in volts
bias_step = .5
# bias compliance
bias_comp = 1000e-6
# bias limit
bias_limit = 70
# bias_threshold
bias_thresh = 1000e-6
bias_volt = 5
bias_curr = 1

# contact voltage
cont_volt = 200e-3
# contact current threshold
cont_thresh = 50e-9
# contact compliance
cont_comp = 1e-6
cont_curr = 1

cont_currs = []
bias_currs = []

bias_vs = []

bias_dcs = []
cont_dcs = []


#### ******* SPECIAL FUNCTIONS ************
def quick_read_curr(inst, volt):
    inst.set_volt(volt)
    curr = inst.read_curr()
    inst.set_volt(0)
    return curr

def printStatus():
    global bias_kt, cont_kt, bias_start, bias_step, bias_limit, bias_backoff, bias_comp, cont_volt, cont_thresh, cont_comp, num_cyc,bias_volt,cont_curr
    print('BV:  {}\nBI:  {}\nBR:  {:,}\nCI:  {}\nCR:  {:,}'.format(bias_volt,bias_curr,bias_volt/bias_curr,cont_curr,cont_volt/cont_curr))

# ******* START SETUP *********
# setup file to write to
logs_folder_path = "C:\\Users\\MOLNAR_PH330_D1\\Desktop\\NZERO\\python_code\\logs\\"
now = time.strftime('%Y%m%d_%H%M%S')
# total log
log_fn = "{}{}_{}_{}_{}_log.txt".format(logs_folder_path, device_name, now, bias_step, cont_volt)
# less detailed
data_fn = "{}{}_{}_{}_{}_data.txt".format(logs_folder_path, device_name, now, bias_step, cont_volt)

if os.path.exists(log_fn):
    print("You've gone back in time? File already exists")
    sys.exit(0)
# setup logging
formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d, %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
log = logging.getLogger()
log.setLevel(logging.INFO)
hdlr1 = logging.FileHandler(log_fn)
hdlr1.setFormatter(formatter)
hdlr1.setLevel(logging.INFO)
log.addHandler(hdlr1)

data = logging.getLogger('data')
hdlr2 = logging.FileHandler(data_fn)
hdlr2.setFormatter(formatter)
data.addHandler(hdlr2)

## info goes only to log
## warn goes to data and log

# lets us talk to GPIB
log.info('setting up resource manager')
rm = visa.ResourceManager()

# gives us an instrument to work with
log.info('getting instruments')
inst_bias = rm.open_resource(bias_keithley_addr)
inst_cont = rm.open_resource(cont_keithley_addr)

# uses the module to be able to set/read volt/etc from tool
log.info('instantiating and resetting keithley\'s')
bias_kt = kt.KT2400(inst_bias)
cont_kt = kt.KT2400(inst_cont)
#bias_kt.reset()
#cont_kt.reset()
print('starting measurement')


    
def main():
    global bias_kt, cont_kt, bias_start, bias_step, bias_limit, bias_backoff, bias_comp, cont_volt, cont_thresh, cont_comp, num_cyc,bias_volt,bias_curr,cont_curr
    ##### ******* START MEASUREMENT INITIALIZATION *******
    print('starting initialization')
    ## Initialize
    # set keithley's to volt source mode
    logging.info('setting both kts to volt source mode')
    bias_kt.set_mode('VOLT')
    cont_kt.set_mode('VOLT')

    # set bias keithley range higher to accomdate high measurements
    logging.info('changing volt range on bias')
    bias_kt.set_volt_range(210)

    # Initialize bias keithley
    logging.info('bias keithley volt zero and output on')
    bias_volt = bias_start
    bias_kt.set_volt(bias_volt)
    bias_kt.set_curr_comp(bias_comp)
    bias_kt.set_output('ON')

    # Initialize contact keithley
    logging.info('curr keithley volt zero and output on')
    cont_kt.set_volt(0)
    cont_kt.set_curr_comp(cont_comp)
    cont_kt.set_output('ON')



    bias_turnon = 0
    bias_turnoff = 0
    cont_cturnon = 0
    cont_cturnoff = 0

   
    ##### ******* STARTING MEASUREMENT ********
    
    print('**About to test switch {}. Do you want to continue?\n'.format(device_name))
    raw_input('*Press enter to start test\n')
    bias_kt.beep(740,0.5)
    log.info('testing switch')
    # reset keithley's to 0
    bias_volt = bias_start
    bias_kt.set_volt(bias_volt)
    cont_kt.set_volt(0)
    # read currents
    cont_curr = quick_read_curr(cont_kt, cont_volt)
    bias_curr = bias_kt.read_curr()

    worked = 1
    if abs(cont_curr) >= cont_thresh:
        if abs(bias_curr) > bias_thresh:
            print('MSB and contact shorted from the start')
            printStatus()
            log.info('MSB and contact is shorted from start')
            worked=0
            data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
        else:
            print('contact shorted from the start')
            printStatus()
            log.info('contact is shorted from start')
            worked=0
            data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
    elif abs(bias_curr) > bias_thresh:
        print('MSB shorted from start')
        log.info('MSB is shorted from start')
        worked=0
        data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))

    ##### ***** START SWEEP *****
    else:
        # start sweeping up
        while abs(cont_curr) < cont_thresh:
            #time.sleep(.5)

            # Check if bias voltage too high
            if(bias_volt > bias_limit):
                print("seems like it's an open switch")
                printStatus()
                log.info("seems like it's an open switch")
                worked=0
                break
            
            # increase bias
            bias_volt += bias_step
            # set bias voltage
            bias_kt.set_volt(bias_volt)
            
            # *** If you want a delay at each step
            #time.sleep(.5)

            # *** If you want to set bias to 0 at each step
            #bias_kt.set_volt(0)
            
            # check if contact shorted
            cont_curr = quick_read_curr(cont_kt, cont_volt)
            bias_curr = bias_kt.read_curr()
            cont_currs.append(cont_curr)       
            bias_currs.append(bias_curr)
            bias_vs.append(bias_volt)
            data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
            
            # check if bad switch
            if abs(bias_curr) > bias_thresh:
                print('MSB shorted at {} V'.format(bias_volt))
                printStatus()
                log.info('MSB shorted')
                worked=0
                break
            if abs(bias_curr) > bias_thresh and abs(cont_curr) >= cont_thresh:
                print('MSB and contact shorted')
                printStatus()
                log.info('MSB and contact shorted')
                worked=0
                break
            #time.sleep(0.5)

        printStatus()
        bias_turnon = bias_volt
        cont_cturnon = cont_curr

        # Start sweeping down
        log.info('Start sweep down')
        while(bias_volt > 0):
            # decrease bias
            bias_volt -= bias_step
            # set bias voltage
            bias_kt.set_volt(bias_volt)

            # read currents and log
            cont_curr = quick_read_curr(cont_kt, cont_volt)
            bias_curr = bias_kt.read_curr()
            cont_dcs.append(cont_curr)   
            bias_dcs.append(bias_curr)
            # check when current drops low
            if(cont_curr < 1e-9):
                bias_turnoff = bias_volt
                cont_cturnoff = cont_curr
            data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
            printStatus()
                    
    # reach this point after returning to 0

    

    
    # first make sure bias is off
    bias_kt.set_volt(0)


    
    if worked:
        print('{} contact switched at {} V with {} A'.format(device_name, bias_turnon, cont_cturnon))
        #printStatus()
        data.warn('{} contact switched at {} V with {} A'.format(device_name, bias_turnon, cont_cturnon))
        print('{} contact unswitched at {} V with {} A'.format(device_name, bias_turnoff, cont_cturnoff))
        data.warn('{} contact unswitched at {} V with {} A'.format(device_name, bias_turnoff, cont_cturnoff))
    
    # beep to know test is done
    bias_kt.beep(523,0.5)

    log.info('end backoff {}, {}'.format(bias_volt, cont_curr))

    # this to clear keithley screen
    bias_curr = bias_kt.read_curr()
    cont_curr = quick_read_curr(cont_kt, cont_volt)
    
    bias_curr = bias_kt.read_curr()
    cont_curr = quick_read_curr(cont_kt, cont_volt)
            

    #at this point have finished testing whole chip
    cont_kt.set_volt(0)

    bias_dcs.reverse()
    cont_dcs.reverse()

    plt.figure()

    plt.subplot(2,1,1)
    plt.plot(bias_vs,bias_currs)
    
    plt.plot(bias_vs,bias_dcs)
    plt.title('bias currents')

    plt.subplot(2,1,2)
    plt.title('contact currents')
    plt.plot(bias_vs,cont_currs)
    plt.plot(bias_vs,cont_dcs)

    plt.show()


# so that when ctrl+c, files will still close and voltage resets

try:
    main()
except KeyboardInterrupt:
    bias_kt.set_volt(0)
    cont_kt.set_volt(0)
    
    plt.figure()

    plt.subplot(2,1,1)
    plt.plot(bias_vs,bias_currs)
    plt.title('bias currents')

    plt.subplot(2,1,2)
    plt.title('contact currents')
    plt.plot(bias_vs,cont_currs)

    plt.show()
    print('closed with ctrl+c')
    log.info('closed with ctrl+c')
    hdlr1.close()
    hdlr2.close()
    sys.exit(0)
