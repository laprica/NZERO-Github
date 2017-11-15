import visa
import numpy as np
import time
import os.path
import sys
import keithley2400 as kt
import logging
import xlwt
 
""" Script to do contact pulse sweep test of NZERO NEMS Switch """
""" This is modified to be able to test a chip quickly """
""" A1 through G8, test each switch once"""
 
""" Created by Leanna Pancoast 27 Feb 2017 """

 
#### ******* VARIABLES TO SET *************
# change these to set address
# use rm.list_resources() in shell to see
bias_keithley_addr = 'GPIB0::25::INSTR'
cont_keithley_addr = 'GPIB0::2::INSTR'
 
 
 
chip_name = 'excel_output_test1'
 
col_list = ['A','B','C','D','E','F','G']
row_list = [1,2,3,4,5,6,7,8]
 
 
# starting bias voltage
bias_start = 0
# bias step in volts
bias_step = .5
# bias compliance
bias_comp = 1e-6
# bias limit
bias_limit = 60
# bias_threshold
bias_thresh = 1e-6
 
# contact voltage
cont_volt = 200e-3
# contact current threshold
cont_thresh = 100e-12
# contact compliance
cont_comp = 1e-6
 
 
#### ******* SPECIAL FUNCTIONS ************
def quick_read_curr(inst, volt):
    inst.set_volt(volt)
    curr = inst.read_curr()
    inst.set_volt(0)
    return curr
 
 
 
# ******* START SETUP *********
# setup file to write to
logs_folder_path = "C:\\Users\\MOLNAR_PH330_D1\\Desktop\\NZERO\\python_code\\logs\\"
mat_folder_path = "C:\\Users\\MOLNAR_PH330_D1\\Desktop\\NZERO\\python_output\\"
now = time.strftime('%Y%m%d_%H%M%S')
# total log
log_fn = "{}{}_{}_{}_{}_log.txt".format(logs_folder_path, chip_name, now, bias_step, cont_volt)
# less detailed
data_fn = "{}{}_{}_{}_{}_data.txt".format(logs_folder_path, chip_name, now, bias_step, cont_volt)
 
# for final table of values
mat_fn = "{}{}_{}_on_values.txt".format(mat_folder_path, chip_name, now)
cs_fn = "{}{}_{}_summary.txt".format(mat_folder_path, chip_name, now)
 
if os.path.exists(log_fn):
    print("You've gone back in time? File already exists")
    sys.exit(0)
if os.path.exists(mat_fn):
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
 
# store the on voltages, contact current, bias current
bias_v = []
cont_i = []
bias_i = []
stat1 = []
stat2 = []
 
# info goes only to log
# warn goes to data and log
 
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
 
def test_device():
    global bias_kt, cont_kt, bias_start, bias_step, bias_limit, bias_backoff, bias_comp, cont_volt, cont_thresh, cont_comp,bias_v,cont_i,bias_i,stat1,stat2
    log.info('testing switch')
    # reset keithley's to 0
    bias_volt = 0
    bias_kt.set_volt(bias_volt)
    cont_kt.set_volt(0)
    # read currents
    cont_curr = quick_read_curr(cont_kt, cont_volt)
    bias_curr = bias_kt.read_curr()
 
    worked = 1
    if abs(cont_curr) >= cont_thresh:
        if abs(bias_curr) > bias_thresh:
            stat1.append('SDC')
            stat2.append('{}'.format(bias_volt))
            worked = 0
            print('MSB and contact shorted from the start')
            log.info('MSB and contact is shorted from start')
            data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
        else:
            stat1.append('SC')
            stat2.append('{}'.format(bias_volt))
            worked = 0
            print('contact shorted from the start')
            log.info('contact is shorted from start')
            data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
    elif abs(bias_curr) > bias_thresh:
        stat1.append('SD')
        stat2.append('{}'.format(bias_volt))
        worked = 0
        print('MSB shorted from start')
        log.info('MSB is shorted from start')
        data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
    else:
        # actually do the sweep
        while abs(cont_curr) < cont_thresh:
            if(bias_volt > bias_limit):
                stat1.append('o')
                stat2.append('')
                worked = 0
                print("seems like it's an open switch")
                log.info("seems like it's an open switch")
                break
            
            # increase bias
            bias_volt += bias_step
            # set bias voltage
            bias_kt.set_volt(bias_volt)
            # check if contact shorted
            cont_curr = quick_read_curr(cont_kt, cont_volt)
            bias_curr = bias_kt.read_curr()
            data.warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
            # check if bad switch
            if abs(bias_curr) > bias_thresh and abs(cont_curr) >= cont_thresh:
                stat1.append('SDC')
                stat2.append('{}'.format(bias_volt))
                worked = 0
                print('MSB and contact shorted')
                log.info('MSB and contact shorted')
                break
 
            if abs(bias_curr) > bias_thresh:
                stat1.append('SD')
                stat2.append('{}'.format(bias_volt))
                worked = 0
                print('MSB shorted at {} V'.format(bias_volt))
                log.info('MSB shorted')
                break
            
    bias_v.append(bias_volt)
    cont_i.append(cont_curr)
    bias_i.append(bias_curr)
                    
    # reach this point after sweep exits
 
    # first make sure bias is off
    bias_kt.set_volt(0)
    
    if worked:
        stat1.append('~{}'.format(bias_volt))
        stat2.append('({:.4f})'.format(cont_curr*1e6))
        print('switched at {} V with {} A'.format(bias_volt, cont_curr))
        data.warn('switched at {} V with {} A'.format(bias_volt, cont_curr))
    
    
    log.info('end backoff {}, {}'.format(bias_volt, cont_curr))
 
    # this to clear keithley screen
    bias_curr = bias_kt.read_curr()
    cont_curr = quick_read_curr(cont_kt, cont_volt)
 
 
 
print('Measuring chip {}'.format(chip_name))
 
    
def main():
    global bias_kt, cont_kt, bias_start, bias_step, bias_limit, bias_backoff, bias_comp, cont_volt, cont_thresh, cont_comp, num_cyc
    ##### ******* START MEASUREMENT INITIALIZATION *******
    print('Initialization')
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
 
#    cont_curr = quick_read_curr(cont_kt, cont_volt)
 
   
    ##### ******* STARTING MEASUREMENT ********
    for col in col_list:
        for row in row_list:
            bias_kt.beep(740,0.5)
            raw_input('**About to test switch {}{}. Press Enter to continue.\n'.format(col,row))
            logging.info('testing switch {}{}'.format(col,row))
            test_device()
            # beep to know test is done
            bias_kt.beep(523,0.5)
            raw_input('\n**Finished testing {}{}. Press Enter to continue.\n'.format(col,row))
                    
    # reach this point after testing whole chip
    logging.info('finished whole chip')
    print('Finished testing all switches on {}.\n'.format(chip_name))
            
    logging.info('Testing complete! :D')
    
 
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
 
 
 
 
 
 
 
