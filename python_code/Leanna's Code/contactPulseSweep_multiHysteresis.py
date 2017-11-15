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



device_name = 'SOI8-10-M1R-13-F3_2cyc'



# starting bias voltage
bias_start = 0
# bias step in volts
bias_step = .25
# bias compliance
bias_comp = 1000e-6
# bias limit
bias_limit = 60
# bias_threshold
bias_thresh = 1000e-6
bias_volt = 5
bias_curr = 1

# contact voltage
cont_volt = 200e-3
# contact current threshold
cont_thresh = 1e-9
cont_dthresh = .1e-9
# contact compliance
cont_comp = 1e-6
cont_curr = 1

numCycles = 2
cycToPrint = 1

cont_currs = []
bias_vs = []


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
logs_folder_path = "C:\\Users\\MOLNAR_PH330_D1\\Desktop\\NZERO\\python_code\\logs\\SOI8-10-M1R-13\\10 cycle test\\"
now = time.strftime('%Y%m%d_%H%M%S')
# total log
log_fn = "{}{}_{}_{}_{}_log.txt".format(logs_folder_path, device_name, now, bias_step, cont_volt)
# less detailed
data_fn = "{}{}_{}_{}_{}_data.txt".format(logs_folder_path, device_name, now, bias_step, cont_volt)
50e-9
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
    global bias_kt, cont_kt, bias_start, bias_step, bias_limit, bias_backoff, bias_comp, cont_volt, cont_thresh, cont_comp, num_cyc,bias_volt,bias_curr,cont_curr,bias_vs,cont_currs
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
    bias_rOff = 0
    bias_rOn = 0
    cont_rOn = 0
    cont_rOff = 0

   
    ##### ******* STARTING MEASUREMENT ********
    
    print('**About to test switch {}. Do you want to continue?\n'.format(device_name))
    raw_input('*Press enter to start test\n')
    bias_kt.beep(740,0.5)
    log.info('testing switch')
    log.info('start {} cycles'.format(numCycles))
            
    for i in range(numCycles):
        log.info('starting cycle {}'.format(i+1))
        
        # reset keithley's to 0
        bias_volt = bias_start
        bias_kt.set_volt(bias_volt)
        cont_kt.set_volt(0)
        time.sleep(1)
        
        # read currents
        cont_curr = quick_read_curr(cont_kt, cont_volt)
        bias_curr = bias_kt.read_curr()

        worked = 1

        # check initial numbers
        if abs(cont_curr) >= cont_thresh:
            if abs(bias_curr) > bias_thresh:
                print('MSB and contact shorted from the start')
                log.info('MSB and contact is shorted from start')
                worked=0
                data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
            else:
                print('contact shorted from the start')
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
            ## ** start sweeping up
            while abs(cont_curr) < cont_thresh:
                #time.sleep(.5)

                # Check if bias voltage too high
                if(bias_volt > bias_limit):
                    print("seems like it's an open switch")
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

                # add to graph to plot
                cont_currs.append(cont_curr)
                bias_vs.append(bias_volt)
                
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

            # record info
            bias_turnon = bias_volt
            bias_rOn = bias_volt/bias_curr
            cont_cturnon = cont_curr
            cont_rOn = cont_volt/cont_curr

            bias_start = 0
            

##            #### ***** Start sweeping down
##            off = 0
##            log.info('Start sweep down')
##            while(off != 1 and bias_volt > 0):
##                # decrease bias
##                bias_volt -= bias_step
##                # set bias voltage
##                bias_kt.set_volt(bias_volt)
##
##                # read currents and log
##                cont_curr = quick_read_curr(cont_kt, cont_volt)
##                bias_curr = bias_kt.read_curr()
##                
##                # check when current drops low
##                if(bias_volt == 0 or cont_curr < cont_dthresh):
##                    off = 1
##                    bias_turnoff = bias_volt
##                    bias_rOff = bias_volt/bias_curr
##                    cont_cturnoff = cont_curr
##                    cont_rOff = cont_volt/cont_curr
##                    #print bias_volt
##                    #print bias_start
##                    bias_start = bias_volt - 10*bias_step
##                    if(bias_start < 0):
##                        bias_start = 0
##                    #print 'blah {}\n'.format(bias_start)
##            #### ***** end sweeping down

                    
            # reach this point after returning to 0 V
            if(i % cycToPrint == 0):
                print('Cycle {}:\nVon: {:,}\nVoff: {:,}\nbiasOnR: {:,}\nbiasOffR: {:,}\ncontOnR: {:,}\ncontOffR: {:,}\n'.format(i+1, bias_turnon,bias_turnoff,bias_rOn,bias_rOff,cont_rOn,cont_rOff))
            data.warn('{},{},{},{},{},{},{}'.format(i+1, bias_turnon,bias_turnoff,bias_rOn,bias_rOff,cont_rOn,cont_rOff))

            # cycle to beginning of numCycle loop

##            plt.figure()
##            plt.title('Cycle {}'.format(i+1))
##            plt.plot(bias_vs,cont_currs)
##            plt.show()

    
    ## ** End numCycles here
        
    # first make sure bias is off
    bias_kt.set_volt(0)

    
    # beep to know test is done
    bias_kt.beep(523,0.5)

    log.info('end numCycles loop')

    # this to clear keithley screen
    bias_curr = bias_kt.read_curr()
    cont_curr = quick_read_curr(cont_kt, cont_volt)
    
    bias_curr = bias_kt.read_curr()
    cont_curr = quick_read_curr(cont_kt, cont_volt)
            
    cont_kt.set_volt(0)

    hdlr1.close()
    hdlr2.close()


# so that when ctrl+c, files will still close and voltage resets

try:
    main()
except KeyboardInterrupt:
    bias_kt.set_volt(0)
    cont_kt.set_volt(0)
    print('closed with ctrl+c')
    log.info('closed with ctrl+c')
    hdlr1.close()
    hdlr2.close()
    sys.exit(0)
