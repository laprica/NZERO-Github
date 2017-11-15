"""
Date: 2017/07/19
Written by: Hyun Kyo Jung
Description: Module for object oriented fashion of saving data for each device / chip
             for the NZERO switch pulse sweep testing.
"""

class chip(object):
    """Class for a chip, it stores information about the chip being tested.
    name: (String) chip name
    auto: (bool) test mode
    log: (logger)
    data: (data logger)
    hdlr1: (log handler for log)
    hdlr2: (log handler for data)
    path: (file path for the data log)
    """
#stat1=[], stat2=[], bias_v=[], cont_i=[], bias_i=[],
    def __init__(self, name="", auto=False,  log="", data = '',
                 hdlr1='', hdlr2='', path=''):
        self.name = name
        self.auto = auto
        self.stat1 = []
        self.stat2 = []
        self.bias_v = []
        self.cont_i = []
        self.bias_i = []
        self.log = log
        self.data = data
        self.hdlr1 = hdlr1
        self.hdlr2 = hdlr2
        self.path = path
        self.devices = []
        for i in range(0, 56):
            self.stat1.append("not tested")
            self.stat2.append("not tested")
            self.bias_v.append("not tested")
            self.cont_i.append("not tested")
            self.bias_i.append("not tested")
            self.devices.append(device())
        
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name

    def get_auto(self):
        return self.auto
    def set_auto(self, auto):
        self.auto = auto

    def get_stat1(self):
        return self.stat1
    def set_stat1(self, i, v):
        self.stat1[i] = v

    def get_stat2(self):
        return self.stat2  
    def set_stat2(self, i, v):
        self.stat2[i] = v

    def get_bias_v(self):
        return self.bias_v
    def set_bias_v(self, i, v):
        self.bias_v[i] = v

    def get_cont_i(self):
        return self.cont_i
    def set_cont_i(self, i, v):
        self.cont_i[i] = v

    def get_bias_i(self):
        return self.bias_i
    def set_bias_i(self, i, v):
        self.bias_i[i] = v

    def get_log(self):
        return self.log
    def set_log(self, log):
        self.log = log

    def get_data(self):
        return self.data
    def set_data(self, data):
        self.data = data

    def get_hdlr1(self):
        return self.hdlr1
    def set_hdlr1(self, hdlr1):
        self.hdlr1 = hdlr1

    def get_hdlr2(self):
        return self.hdlr2
    def set_hdlr2(self, hdlr2):
        self.hdlr2 = hdlr2

    def get_path(self):
        return self.path
    def set_path(self, path):
        self.path = path

    def get_devices(self):
        return self.devices

    def get_device(self, txt):
        """txt: a1(A1),...,a8(A8),...,g8(G8)
           Returns the correct device object."""

        #this index enables us to store data in
        #the right index of our data-storing arrays
        index = 0;
        if ord(txt[0]) < 97:
            index = (ord(txt[0])-65) * 8 + int(txt[1]) - 1
        else:
            index = (ord(txt[0])-97) * 8 + int(txt[1]) - 1
        return self.get_devices()[index]

    

    def __str__(self):
        return "chip name: " + self.name + "\ntest mode: " + str(self.auto)
    

class device(chip):
    """Represents each device in a chip"""
    """name: name of the a device A-G+1-8"""
    """stat1: o, SC, SDC, SD when there is an error, or cont_i when switched."""
    """stat2: always bias_volt"""
    def __init__(self, name='', stat1='', stat2=0):
        self.name = name
        self.stat1 = stat1
        self.stat2 = stat2

    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_stat1(self):
        return self.stat1
    def set_stat1(self, stat1):
        self.stat1 = stat1
    def get_stat2(self):
        return self.stat2
    def set_stat2(self, stat2):
        self.stat2 = stat2
    def __str__(self):
        return "device #: " + self.name + "\nstat1: " + str(self.stat1) + "\nstat2: " + str(self.stat2)
    
