# This file works with an Arduino Due to test
# an NZERO RF NEMS Switch with the DC-TIA Test.

# Written by Leanna Pancoast
# 9 Nov 2017
# Cornell University
# Inspiration by the Girino project by Cristiano Lino Fontana

import serial
from struct import unpack
import numpy as np
import logging
from matplotlib import pyplot as plt
import time
import os.path
import sys

# ******* START SETUP ********

# *** SERIAL ***
# open serial port
print('Starting Serial port')
stream = serial.Serial('COM3',9600)




#### ******* STARTING MEASUREMENT *******
# want to make sure can control arduino with python

kb = raw_input("Would you like to continue? (y/n)")

while (kb == 'y'):
    kb = raw_input("number between 0 and 5 V")
    stream.write(kb)
    kb = raw_input("Would you like to continue? (y/n)")

print "finished"

stream.close()


