# This file works with an Arduino Due to test
# an NZERO RF NEMS Switch with the DC-TIA Test.

# Written by Leanna Pancoast
# 9 Nov 2017
# Cornell University
# Inspiration by the Girino project by Cristiano Lino Fontana

import serial
#from struct import unpack
#import numpy as np
#import logging
#from matplotlib import pyplot as plt
import time
import os.path
import sys

# initial setup things

device_name = 'SOI8-10-M1R-11-E2'

# starting gate voltage
gate_start = 0
# gate step in volts
gate_step = 0.5
# gate limit (max voltage to apply)
gate_limit = 60

gate_vs = []
source_vs = []


# ******* START SETUP ********
# *** LOGGING ***
# setup logging
#logs_folder_path = "C:\\Users\\MOLNAR_PH330_D1\\Desktop\\NZERO\\TIA Automation\\logs\\"
#now = time.strftime('%Y%m%d_%H%M%S')
# complete log
#log_fn = "{}{}_{}_log.txt".format(logs_folder_path, device_name, now)
#data_fn = "{}{}_{}_data.txt".format(logs_folder_path, device_name, now)

if os.path.exists(log_fn):
    print("you've gone back in time? File already exists")
    sys.exit(0)

# setup logging
#formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d, %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
#log = logging.getLogger()
#log.setLevel(logging.INFO)
#hdlr1 = logging.FileHandler(log_fn)
#hdlr1.setFormatter(formatter)
#hdlr1.setLevel(logging.INFO)
#log.addHandler(hdlr1)
#
#data = logging.getLogger('data')
#hdlr2 = logging.FileHandler(data_fn)
#hdlr2.setFormatter(formatter)
#data.addHandler(hdlr2)


# *** SERIAL ***
# open serial port
print('Starting Serial port')
#log.info('Starting Serial Port')
stream = serial.Serial( 'COM5',115200,timeout=5)
time.sleep(0.5)
line = ''
while line.find("Ready") == -1:
    line = stream.readline()

print('teehee')
print line


### *** HELPER FUNCTIONS ***

def checkFail(line):
    if( line.find("killed") != -1):
        print("Kill switch activated")
        return 1
        
    if( line.find("up failed") != -1):
        print("ramp up failed")
        return 1
    
    if( line.find("down failed") != -1):
        print("ramp down failed")
        return 1
    
    if ( line.find("Shorted") != -1 ):
        print("Shorted from start {}".format(stream.readline()))
        return 1
    if( line.find("open") != -1):
        print("Open switch")
        return 1
    if( line.find("stuck") != -1):
        print("stuck switch")
        return 1
    if( line.find("stopped") != -1):
        print("stopped switch")
        return 1
    if( line.find("End") != -1):
        print("End Program")
        return 1

def main():
    global gate_start, gate_step, gate_limit, gate_vs, source_vs, line

    #### ***** START MEASUREMENT INITIALIZATION *****
    # give the sweep parameters to the Due
    #stream.write('p')
    #stream.write(gate_start)
    #stream.write('{}'.format(gate_step))
    #stream.write(gate_limit)
    #line = stream.readline()
    #print('blah')
    #line = stream.readline()
    #print(line)
    

    #### ******* STARTING MEASUREMENT *******
    print("** About to test switch {}. Do you want to continue?\n".format(device_name))
    raw_input("*Press enter to start test\n")
#    log.info("Testing switch")
    # Tell Due to Begin the sweep
    stream.write('b')
    line = stream.readline()
    print('wrote b\n')
    
    checkFail(line)
    
    while(not checkFail(line)):
        
        if (line.find('Closed') != -1):
            vG = stream.readline()
            vS = stream.readline()
            print( "device closed at {} V with {} Vo".format(vG, vS))
            
        elif (line.find('Opened') != -1):
            vG = stream.readline()
            vS = stream.readline()
            print( "device closed at {} V with {} Vo".format(vG, vS))
        
        
        else:
            #vGa = line
            vGb = stream.readline()
            vS = stream.readline()
    
    
            gate_vs.append(vGb)
            source_vs.append(vS)
            print('gate V: {}, source V: {}\n'.format(vGb, vS))
    
        line = stream.readline()


    print('done!')

    stream.close()
#    hdlr1.close()
#    hdlr2.close()


try :
    main()
except KeyboardInterrupt:
    # set everything to 0 if interrupted with keyboard
    print('closed with ctrl+c')
#    log.info('closed with ctrl+c')
    stream.write('s')
    stream.close()
#    hdlr1.close()
#    hdlr2.close()

