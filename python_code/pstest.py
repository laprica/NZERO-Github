from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.garden.graph import Graph, MeshLinePlot
import visa
import time
import sys
import keithley2400 as kt
import logging
import popup
import test
import myFormatter
 
""" Script to do contact pulse sweep test of NZERO NEMS Switch """
""" This is modified to be able to test a chip in both manual and automatic means. """
""" GUI has been added to make the testing more efficient, informative, flexible, and controlled."""
""" Each cell alloted for a device is a button that will show the result when clicked. """
 
""" Code originally created by Leanna Pancoast 27 Feb 2017 """
""" modified by Hyun Kyo Jung 17 Jul 2017 """

#Initializing a chip object and 56 device objects.
tst = test.chip()
 
# change these to set address
# use rm.list_resources() in shell to see
bias_keithley_addr = 'GPIB0::25::INSTR'
cont_keithley_addr = 'GPIB0::2::INSTR'

# setup file to write to
logs_folder_path = "C:\\Users\\MOLNAR_PH330_D1\\Desktop\\NZERO\\python_code\\logs\\"
now = time.strftime('%Y%m%d_%H%M%S')
            
# setup logging (info goes only to log, warn goes to data and log)
formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d, %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
#formatter = myFormatter.myFormatter()
log = logging.getLogger()
log.setLevel(logging.INFO)
tst.set_log(log)
         
data = logging.getLogger('data')
#data.setLevel(logging.INFO)
tst.set_data(data)
# lets us talk to GPIB
logging.info('setting up resource manager')         
print('setting up resource manager')
rm = visa.ResourceManager()
             
# gives us an instrument to work with
logging.info('getting instruments')
print('getting instruments')
inst_bias = rm.open_resource(bias_keithley_addr)
inst_cont = rm.open_resource(cont_keithley_addr)

# uses the module to be able to set/read volt/etc from tool
logging.info('instantiating and resetting keithley\'s')
print('instantiating and resetting keithley\'s')
bias_kt = kt.KT2400(inst_bias)
cont_kt = kt.KT2400(inst_cont)
#bias_kt.reset()
#cont_kt.reset()

#### ******* VARIABLES TO SET *************
col_list = ['A','B','C','D','E','F','G']
row_list = [1,2,3,4,5,6,7,8]
 
# starting bias voltage
bias_start = 0
# bias step in volts
bias_step = .5
# bias compliance
bias_comp = 1e-6
# bias limit
bias_limit = 50.0                       #################change this value before real testing.
# bias_threshold
bias_thresh = 900e-9
 
# contact voltage
cont_volt = 200e-3
# contact current threshold
cont_thresh = 100e-9
# contact compliance
cont_comp = 1e-6 
 
#CONSTANTS for Messages to be shown in the prompt screen.
msg_chip = "Type in the chip name\n and press enter."
msg_mode_option = "Type in the testing option. \n manual or auto."
msg_start = "Press enter\n to start the test."
msg_auto_test = "Press enter\n to test the next device."
msg_manual_test = "Type in the device\n to test and press enter."


class MeasureRoot(BoxLayout):
    """This is the root layout class for the kivy GUI. """
    def process_input(self, txt):
        """this method takes the user input in the textinput box and processes."""
        """if the actual test has not begun, it calls the start_test method from"""
        """OtherInfoForm, its child layout, to gather and update test info."""
        """Once test has begun, it calls the test_device(txt) in MeasureChipForm."""
        print len(self.secondbox.device.text)
        if ((self.firstbox.prompt_screen.text == msg_auto_test)
                                                | (self.firstbox.prompt_screen.text == msg_manual_test)):
            self.secondbox.test_device(txt)
        else:
            self.firstbox.start_test(txt)
 
    def set_focus(self, dt):
        """sets the focus to the textinput widget after enter/click. """
        self.secondbox.input.focus = True
 
    def set_focus_real(self):
        """calls the set_focus method once after 0.5 second interval. The focus must be returned
        after short interval so this method is necessary."""
        Clock.schedule_once(self.set_focus, 0.5)
 
    def close_window(self):
        """closes the GUI window"""
        Window.close()
 
    def reset_test(self):
        """clears the testing GUI screen to the original set-up. """
        """enables testing of another chip without having the exit."""
        self.firstbox.prompt_screen.text = msg_chip
        self.secondbox.device.text = "device tested last: "
        self.firstbox.chip_name.text = "The chip being tested: "
        self.firstbox.test_modes.manual.state = 'normal'
        self.firstbox.test_modes.auto.state = 'normal'
        if len(self.firstbox.real_graph.plots) == 1:
                self.firstbox.real_graph.remove_plot(self.firstbox.real_graph.plots[0])
        #empty out the test results from last chip.
        self.secondbox.test_result.a.a1.text = ''
        self.secondbox.test_result.a.a2.text = ''
        self.secondbox.test_result.a.a3.text = ''
        self.secondbox.test_result.a.a4.text = ''
        self.secondbox.test_result.a.a5.text = ''
        self.secondbox.test_result.a.a6.text = ''
        self.secondbox.test_result.a.a7.text = ''
        self.secondbox.test_result.a.a8.text = ''
        self.secondbox.test_result.b.b1.text = ''
        self.secondbox.test_result.b.b2.text = ''
        self.secondbox.test_result.b.b3.text = ''
        self.secondbox.test_result.b.b4.text = ''
        self.secondbox.test_result.b.b5.text = ''
        self.secondbox.test_result.b.b6.text = ''
        self.secondbox.test_result.b.b7.text = ''
        self.secondbox.test_result.b.b8.text = ''
        self.secondbox.test_result.c.c1.text = ''
        self.secondbox.test_result.c.c2.text = ''
        self.secondbox.test_result.c.c3.text = ''
        self.secondbox.test_result.c.c4.text = ''
        self.secondbox.test_result.c.c5.text = ''
        self.secondbox.test_result.c.c6.text = ''
        self.secondbox.test_result.c.c7.text = ''
        self.secondbox.test_result.c.c8.text = ''
        self.secondbox.test_result.d.d1.text = ''
        self.secondbox.test_result.d.d2.text = ''
        self.secondbox.test_result.d.d3.text = ''
        self.secondbox.test_result.d.d4.text = ''
        self.secondbox.test_result.d.d5.text = ''
        self.secondbox.test_result.d.d6.text = ''
        self.secondbox.test_result.d.d7.text = ''
        self.secondbox.test_result.d.d8.text = ''
        self.secondbox.test_result.e.e1.text = ''
        self.secondbox.test_result.e.e2.text = ''
        self.secondbox.test_result.e.e3.text = ''
        self.secondbox.test_result.e.e4.text = ''
        self.secondbox.test_result.e.e5.text = ''
        self.secondbox.test_result.e.e6.text = ''
        self.secondbox.test_result.e.e7.text = ''
        self.secondbox.test_result.e.e8.text = ''
        self.secondbox.test_result.f.f1.text = ''
        self.secondbox.test_result.f.f2.text = ''
        self.secondbox.test_result.f.f3.text = ''
        self.secondbox.test_result.f.f4.text = ''
        self.secondbox.test_result.f.f5.text = ''
        self.secondbox.test_result.f.f6.text = ''
        self.secondbox.test_result.f.f7.text = ''
        self.secondbox.test_result.f.f8.text = ''
        self.secondbox.test_result.g.g1.text = ''
        self.secondbox.test_result.g.g2.text = ''
        self.secondbox.test_result.g.g3.text = ''
        self.secondbox.test_result.g.g4.text = ''
        self.secondbox.test_result.g.g5.text = ''
        self.secondbox.test_result.g.g6.text = ''
        self.secondbox.test_result.g.g7.text = ''
        self.secondbox.test_result.g.g8.text = ''

    def draw_graph(self, dev, txt):
        """draw graph of test result when a device button is clicked"""
        """x-axis reps bias_volt and y-axis reps cont_curr."""
        if txt != '':
            self.firstbox.device.text = "Summary of: " + dev 
            f = open(tst.get_path(), 'r')
            s = f.read()
            bias_v = []
            cont_i = []

            if len(txt) != 1:
                i1 = s.find(dev) if s.find(dev)!= -1 else s.find(dev[0].upper() + dev[1])
                final_bias_v = tst.get_device(dev).get_stat2()
                i2 = s.find(str(final_bias_v), i1)
                arr = s[i1:i2].split(',')

                i_bias_v = 1
                i_cont_i = 3
                
                while i_cont_i < len(arr):
                    bias_v.append(float(arr[i_bias_v]))
                    cont_i.append(float(arr[i_cont_i][:arr[i_cont_i].find('\n')])*10**12)
                    i_bias_v += 3
                    i_cont_i += 3

            ##if I need to implement button functionality for columns and rows, add if conditions like "if len(txt) == 1"   
                
            if len(self.firstbox.real_graph.plots) == 1:
                self.firstbox.real_graph.remove_plot(self.firstbox.real_graph.plots[0])
            self.plot = MeshLinePlot(color=[1,1,1,1])
            self.firstbox.real_graph.add_plot(self.plot)
            self.plot.points = []
            
            for i, (x, y) in enumerate(zip(bias_v, cont_i)):
                self.plot.points.append((x,y))
                
        
class OtherInfoForm(BoxLayout):
    """child boxlayout of the test GUI (left side)"""
    """Includes prompt screen, chip name, test mode, test summary(graph)"""
    def start_test(self, txt):
        """this method is called whenever the tester presses enter or clicks the enter"""
        """button on the test GUI. Then the text in the textinput is passed along """
        """to be gathered in this boxlayout as preliminary information of the test."""
        """Also, it changes the prompt screen on the GUI as needed."""
        """Importantly, this method calls setup_logging() and test_setup() methods in order."""
    # save chip_name
        if self.prompt_screen.text == msg_chip:
            if txt == '':
                popup.give_warning("please insert correct information.")
            else:
                self.prompt_screen.text = msg_mode_option
                self.chip_name.text = self.chip_name.text + txt
                tst.set_name(txt)
                setup_logging()
    # save test_mode
        elif self.prompt_screen.text == msg_mode_option:
            if ((txt == "Manual")|(txt == "manual")):
                self.test_modes.manual.state = 'down'
                self.test_modes.auto.state = 'normal'
                tst.set_auto(False)
                self.prompt_screen.text = msg_start
            elif ((txt == "Auto") | (txt == "auto")):
                self.test_modes.auto.state = 'down'
                self.test_modes.manual.state = 'normal'
                tst.set_auto(True)
                self.prompt_screen.text = msg_start
            else:
                popup.give_warning("please type in 'manual' or 'auto'")
    # test setup when pressed enter
        else:
            if tst.get_auto():
                self.prompt_screen.text = msg_auto_test
            else:
                self.prompt_screen.text = msg_manual_test
            test_setup()
 
            
class MeasureChipForm(BoxLayout):
    """child boxlayout of the test GUI (right side) that contains the test result buttons,"""
    """a text input, and buttons for enter, finish and reset."""
    def test_device(self, txt):
        """take tester's choice of device and put the test result into the"""
        """appropriate button."""
        try:
        # Manual testing mode
            if not tst.get_auto():
                if ((txt == '') | (len(txt) != 2)):
                    popup.give_warning("please insert correct information.")
                elif ((not txt[0].isalpha()) | (not txt[1].isdigit())):
                    popup.give_warning("please insert correct information.")
                elif (not((ord(txt[0]) in range(65, 72))|(ord(txt[0]) in range(97,104)))&(int(txt[1]) in range(1, 9))):
                    popup.give_warning("please insert correct information.")
                else:
                    self.device.text = "Device tested last: " + txt
                    test_device(txt)
        # Automatic testing mode
            else:
                if self.device.text[-2:] == "G8":
                    print 1
                    popup.give_warning("please press finish button if you have finished testing " +
                                       "or press reset button if you wish to test another chip.")
                elif self.device.text == "device tested last: ":
                    print 2
                    test_device("A1")
                    self.test_result.a.a1.text = str(tst.get_devices()[0].get_stat1()) + ' ' + str(tst.get_devices()[0].get_stat2())
                    self.device.text = "Device tested last: A1"                        
                else:
                    print self.device.text
                    print 3
                    txt = self.device.text[-2:-1] + str(int(self.device.text[-1])+1) if int(self.device.text[-1]) < 8 else str(unichr(ord(self.device.text[-2:-1])+1)) + '1'
                    test_device(txt)
                    self.device.text = "Device tested last: " + txt
        except:
            popup.give_warning("please insert correct information.")
            
        if (txt == "A1") | (txt == "a1"):
            self.test_result.a.a1.text = str(tst.get_devices()[0].get_stat1()) + ' ' + str(tst.get_devices()[0].get_stat2())
        elif (txt == "A2") | (txt == "a2"):  
            self.test_result.a.a2.text = str(tst.get_devices()[1].get_stat1()) + ' ' + str(tst.get_devices()[1].get_stat2())
        elif (txt == "A3") | (txt == "a3"):  
            self.test_result.a.a3.text = str(tst.get_devices()[2].get_stat1()) + ' ' + str(tst.get_devices()[2].get_stat2())
        elif (txt == "A4") | (txt == "a4"):  
            self.test_result.a.a4.text = str(tst.get_devices()[3].get_stat1()) + ' ' + str(tst.get_devices()[3].get_stat2())
        elif (txt == "A5") | (txt == "a5"):  
            self.test_result.a.a5.text = str(tst.get_devices()[4].get_stat1()) + ' ' + str(tst.get_devices()[4].get_stat2())
        elif (txt == "A6") | (txt == "a6"):  
            self.test_result.a.a6.text = str(tst.get_devices()[5].get_stat1()) + ' ' + str(tst.get_devices()[5].get_stat2())
        elif (txt == "A7") | (txt == "a7"):  
            self.test_result.a.a7.text = str(tst.get_devices()[6].get_stat1()) + ' ' + str(tst.get_devices()[6].get_stat2())
        elif (txt == "A8") | (txt == "a8"):  
            self.test_result.a.a8.text = str(tst.get_devices()[7].get_stat1()) + ' ' + str(tst.get_devices()[7].get_stat2())
        elif (txt == "B1") | (txt == "b1"):  
            self.test_result.b.b1.text = str(tst.get_devices()[8].get_stat1()) + ' ' + str(tst.get_devices()[8].get_stat2())
        elif (txt == "B2") | (txt == "b2"):  
            self.test_result.b.b2.text = str(tst.get_devices()[9].get_stat1()) + ' ' + str(tst.get_devices()[9].get_stat2())
        elif (txt == "B3") | (txt == "b3"):  
            self.test_result.b.b3.text = str(tst.get_devices()[10].get_stat1()) + ' ' + str(tst.get_devices()[10].get_stat2())
        elif (txt == "B4") | (txt == "b4"):  
            self.test_result.b.b4.text = str(tst.get_devices()[11].get_stat1()) + ' ' + str(tst.get_devices()[11].get_stat2())
        elif (txt == "B5") | (txt == "b5"):  
            self.test_result.b.b5.text = str(tst.get_devices()[12].get_stat1()) + ' ' + str(tst.get_devices()[12].get_stat2())
        elif (txt == "B6") | (txt == "b6"):  
            self.test_result.b.b6.text = str(tst.get_devices()[13].get_stat1()) + ' ' + str(tst.get_devices()[13].get_stat2())
        elif (txt == "B7") | (txt == "b7"):  
            self.test_result.b.b7.text = str(tst.get_devices()[14].get_stat1()) + ' ' + str(tst.get_devices()[14].get_stat2())
        elif (txt == "B8") | (txt == "b8"):  
            self.test_result.b.b8.text = str(tst.get_devices()[15].get_stat1()) + ' ' + str(tst.get_devices()[15].get_stat2())
        elif (txt == "C1") | (txt == "c1"):  
            self.test_result.c.c1.text = str(tst.get_devices()[16].get_stat1()) + ' ' + str(tst.get_devices()[16].get_stat2())
        elif (txt == "C2") | (txt == "c2"):  
            self.test_result.c.c2.text = str(tst.get_devices()[17].get_stat1()) + ' ' + str(tst.get_devices()[17].get_stat2())
        elif (txt == "C3") | (txt == "c3"):  
            self.test_result.c.c3.text = str(tst.get_devices()[18].get_stat1()) + ' ' + str(tst.get_devices()[18].get_stat2())
        elif (txt == "C4") | (txt == "c4"):  
            self.test_result.c.c4.text = str(tst.get_devices()[19].get_stat1()) + ' ' + str(tst.get_devices()[19].get_stat2())
        elif (txt == "C5") | (txt == "c5"):  
            self.test_result.c.c5.text = str(tst.get_devices()[20].get_stat1()) + ' ' + str(tst.get_devices()[20].get_stat2())
        elif (txt == "C6") | (txt == "c6"):  
            self.test_result.c.c6.text = str(tst.get_devices()[21].get_stat1()) + ' ' + str(tst.get_devices()[21].get_stat2())
        elif (txt == "C7") | (txt == "c7"):  
            self.test_result.c.c7.text = str(tst.get_devices()[22].get_stat1()) + ' ' + str(tst.get_devices()[22].get_stat2())
        elif (txt == "C8") | (txt == "c8"):  
            self.test_result.c.c8.text = str(tst.get_devices()[23].get_stat1()) + ' ' + str(tst.get_devices()[23].get_stat2())
        elif (txt == "D1") | (txt == "d1"):  
            self.test_result.d.d1.text = str(tst.get_devices()[24].get_stat1()) + ' ' + str(tst.get_devices()[24].get_stat2())
        elif (txt == "D2") | (txt == "d2"):  
            self.test_result.d.d2.text = str(tst.get_devices()[25].get_stat1()) + ' ' + str(tst.get_devices()[25].get_stat2())
        elif (txt == "D3") | (txt == "d3"):  
            self.test_result.d.d3.text = str(tst.get_devices()[26].get_stat1()) + ' ' + str(tst.get_devices()[26].get_stat2())
        elif (txt == "D4") | (txt == "d4"):  
            self.test_result.d.d4.text = str(tst.get_devices()[27].get_stat1()) + ' ' + str(tst.get_devices()[27].get_stat2())
        elif (txt == "D5") | (txt == "d5"):  
            self.test_result.d.d5.text = str(tst.get_devices()[28].get_stat1()) + ' ' + str(tst.get_devices()[28].get_stat2())
        elif (txt == "D6") | (txt == "d6"):  
            self.test_result.d.d6.text = str(tst.get_devices()[29].get_stat1()) + ' ' + str(tst.get_devices()[29].get_stat2())
        elif (txt == "D7") | (txt == "d7"):  
            self.test_result.d.d7.text = str(tst.get_devices()[30].get_stat1()) + ' ' + str(tst.get_devices()[30].get_stat2())
        elif (txt == "D8") | (txt == "d8"):  
            self.test_result.d.d8.text = str(tst.get_devices()[31].get_stat1()) + ' ' + str(tst.get_devices()[31].get_stat2())
        elif (txt == "E1") | (txt == "e1"):  
            self.test_result.e.e1.text = str(tst.get_devices()[32].get_stat1()) + ' ' + str(tst.get_devices()[32].get_stat2())
        elif (txt == "E2") | (txt == "e2"):  
            self.test_result.e.e2.text = str(tst.get_devices()[33].get_stat1()) + ' ' + str(tst.get_devices()[33].get_stat2())
        elif (txt == "E3") | (txt == "e3"):  
            self.test_result.e.e3.text = str(tst.get_devices()[34].get_stat1()) + ' ' + str(tst.get_devices()[34].get_stat2())
        elif (txt == "E4") | (txt == "e4"):  
            self.test_result.e.e4.text = str(tst.get_devices()[35].get_stat1()) + ' ' + str(tst.get_devices()[35].get_stat2())
        elif (txt == "E5") | (txt == "e5"):  
            self.test_result.e.e5.text = str(tst.get_devices()[36].get_stat1()) + ' ' + str(tst.get_devices()[36].get_stat2())
        elif (txt == "E6") | (txt == "e6"):  
            self.test_result.e.e6.text = str(tst.get_devices()[37].get_stat1()) + ' ' + str(tst.get_devices()[37].get_stat2())
        elif (txt == "E7") | (txt == "e7"):  
            self.test_result.e.e7.text = str(tst.get_devices()[38].get_stat1()) + ' ' + str(tst.get_devices()[38].get_stat2())
        elif (txt == "E8") | (txt == "e8"):  
            self.test_result.e.e8.text = str(tst.get_devices()[39].get_stat1()) + ' ' + str(tst.get_devices()[39].get_stat2())
        elif (txt == "F1") | (txt == "f1"):  
            self.test_result.f.f1.text = str(tst.get_devices()[40].get_stat1()) + ' ' + str(tst.get_devices()[40].get_stat2())
        elif (txt == "F2") | (txt == "f2"):  
            self.test_result.f.f2.text = str(tst.get_devices()[41].get_stat1()) + ' ' + str(tst.get_devices()[41].get_stat2())
        elif (txt == "F3") | (txt == "f3"):  
            self.test_result.f.f3.text = str(tst.get_devices()[42].get_stat1()) + ' ' + str(tst.get_devices()[42].get_stat2())
        elif (txt == "F4") | (txt == "f4"):  
            self.test_result.f.f4.text = str(tst.get_devices()[43].get_stat1()) + ' ' + str(tst.get_devices()[43].get_stat2())
        elif (txt == "F5") | (txt == "f5"):  
            self.test_result.f.f5.text = str(tst.get_devices()[44].get_stat1()) + ' ' + str(tst.get_devices()[44].get_stat2())
        elif (txt == "F6") | (txt == "f6"):  
            self.test_result.f.f6.text = str(tst.get_devices()[45].get_stat1()) + ' ' + str(tst.get_devices()[45].get_stat2())
        elif (txt == "F7") | (txt == "f7"):  
            self.test_result.f.f7.text = str(tst.get_devices()[46].get_stat1()) + ' ' + str(tst.get_devices()[46].get_stat2())
        elif (txt == "F8") | (txt == "f8"):  
            self.test_result.f.f8.text = str(tst.get_devices()[47].get_stat1()) + ' ' + str(tst.get_devices()[47].get_stat2())
        elif (txt == "G1") | (txt == "g1"):  
            self.test_result.g.g1.text = str(tst.get_devices()[48].get_stat1()) + ' ' + str(tst.get_devices()[48].get_stat2())
        elif (txt == "G2") | (txt == "g2"):  
            self.test_result.g.g2.text = str(tst.get_devices()[49].get_stat1()) + ' ' + str(tst.get_devices()[49].get_stat2())
        elif (txt == "G3") | (txt == "g3"):  
            self.test_result.g.g3.text = str(tst.get_devices()[50].get_stat1()) + ' ' + str(tst.get_devices()[50].get_stat2())
        elif (txt == "G4") | (txt == "g4"):  
            self.test_result.g.g4.text = str(tst.get_devices()[51].get_stat1()) + ' ' + str(tst.get_devices()[51].get_stat2())
        elif (txt == "G5") | (txt == "g5"):  
            self.test_result.g.g5.text = str(tst.get_devices()[52].get_stat1()) + ' ' + str(tst.get_devices()[52].get_stat2())
        elif (txt == "G6") | (txt == "g6"):  
            self.test_result.g.g6.text = str(tst.get_devices()[53].get_stat1()) + ' ' + str(tst.get_devices()[53].get_stat2())
        elif (txt == "G7") | (txt == "g7"):  
            self.test_result.g.g7.text = str(tst.get_devices()[54].get_stat1()) + ' ' + str(tst.get_devices()[54].get_stat2())
        elif (txt == "G8") | (txt == "g8"):  
            self.test_result.g.g8.text = str(tst.get_devices()[55].get_stat1()) + ' ' + str(tst.get_devices()[55].get_stat2())
 
         
class Nzero_Testing_AppApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return MeasureRoot()

#####End of Kivy Classes for GUI#####
 
 
#### ******* SPECIAL FUNCTIONS ************
def quick_read_curr(inst, volt):
    """Returns amount of current flowing at volt"""
    inst.set_volt(volt)
    curr = inst.read_curr()
    inst.set_volt(0)
    return curr
 
def setup_logging():
    """Sets up logging for a test of a chip."""
    """it is called by start_test() and enables creation of separate logs for consecutive testing."""
    if tst.get_log() != "":
        tst.get_log().removeHandler(tst.get_hdlr1())
        tst.get_data().removeHandler(tst.get_hdlr2())
 
    log_fn = "{}{}_{}_{}_{}_log.txt".format(logs_folder_path, tst.get_name(), now, bias_step, cont_volt)
    data_fn = "{}{}_{}_{}_{}_data.txt".format(logs_folder_path, tst.get_name(), now, bias_step, cont_volt)
    hdlr1 = logging.FileHandler(log_fn)
    hdlr1.setLevel(logging.INFO)
    hdlr2 = logging.FileHandler(data_fn)
 
    tst.get_log().addHandler(hdlr1)
    tst.get_data().addHandler(hdlr2)
    tst.set_hdlr1(hdlr1)
    tst.set_hdlr2(hdlr2)
    tst.set_path(data_fn)
    tst.get_data().warn('Date       Time      Voltage(volt) Bias Current(amp) Contact Current(amp)')
    
    hdlr1.setFormatter(formatter)
    hdlr2.setFormatter(formatter)

    
# ******* START SETUP *********
def test_setup():
    """changing set-ups in the keithleys to accomodate the testing."""
    ##### ******* START MEASUREMENT INITIALIZATION *******    
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

 
def test_device(txt):
    """Conduct the pulse-sweep testing of the NZERO NEMS Switch devices."""
    tst.get_device(txt).set_name(txt)
    tst.get_log().info('testing device {}'.format(txt))
    tst.get_data().warn('testing device {} with contact bias (volt) = {}V'.format(txt, cont_volt))
    if tst.get_auto():
        print("auto test for {}".format(txt))
    else:
        print("manual test for {}".format(txt))
    
    #this index enables us to store data in the right index of our data-storing arrays
    index = 0;
    if ord(txt[0]) < 97:
        index = (ord(txt[0])-65) * 8 + int(txt[1]) - 1
    else:
        index = (ord(txt[0])-97) * 8 + int(txt[1]) - 1
            
    # reset keithley's to 0
    bias_volt = 0
    bias_kt.set_volt(bias_volt)
    cont_kt.set_volt(0)
    
    # read currents
    cont_curr = quick_read_curr(cont_kt, cont_volt)
    bias_curr = bias_kt.read_curr()
 
    worked = 1
    issue = ''
    message = ''

    if (abs(cont_curr) >= cont_thresh) &(abs(bias_curr) > bias_thresh):
        issue = 'SDC'
    elif abs(cont_curr) >= cont_thresh:
        issue = 'SC'
    elif abs(bias_curr) > bias_thresh:
        issue = 'SD'

    if issue != '':
        worked = 0
        tst.set_stat1(index, issue)
        tst.set_stat2(index, '{}'.format(bias_volt)) ##
        tst.get_device(txt).set_stat1(issue)
        tst.get_device(txt).set_stat2(bias_volt)
        message = 'MSB and contact shorted from the start' if issue =='SDC' else 'contact shorted from the start' if issue == 'SC' else 'MSB shorted from start'
        print message
        tst.get_log().info(message)
        tst.get_data().warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
     
    else:
        # actually do the sweep
        while abs(cont_curr) < cont_thresh:
            
            if(bias_volt > bias_limit):
                tst.set_stat1(index, 'o')
                tst.set_stat2(index, '')
                tst.get_device(txt).set_stat1('o')
                tst.get_device(txt).set_stat2(bias_volt)
                worked = 0
                print("seems like it's an open switch")
                tst.get_log().info('seems like it\'s an open switch')
                break
            
            # increase bias
            bias_volt += bias_step
            # set bias voltage
            bias_kt.set_volt(bias_volt)
            # check if contact shorted
            cont_curr = quick_read_curr(cont_kt, cont_volt)
            bias_curr = bias_kt.read_curr()
            tst.get_data().warn('{}, {}, {}'.format(bias_volt, bias_curr, cont_curr))
            # check if bad switch
            if abs(bias_curr) > bias_thresh and abs(cont_curr) >= cont_thresh:
                tst.set_stat1(index, 'SDC')
                tst.set_stat2(index, '{}'.format(bias_volt))
                tst.get_device(txt).set_stat1('SDC')
                tst.get_device(txt).set_stat2(bias_volt)
                worked = 0
                print('MSB and contact shorted')
                tst.get_log().info("MSB and contact shorted")
                break
 
            if abs(bias_curr) > bias_thresh:
                tst.set_stat1(index, 'SD')
                tst.set_stat2(index, '{}'.format(bias_volt))
                tst.get_device(txt).set_stat1('SD')
                tst.get_device(txt).set_stat2(bias_volt)
                worked = 0
                print('MSB shorted at {} V'.format(bias_volt))
                tst.get_log().info("MSB shorted")
                break
            
    tst.set_bias_v(index, bias_volt)
    tst.set_cont_i(index, cont_curr)
    tst.set_bias_i(index, bias_curr)
                    
    # reach this point after sweep exits
 
    # first make sure bias is off
    bias_kt.set_volt(0)
    
    if worked:
        tst.set_stat1(index, '{:.4f}'.format(cont_curr*1e6))
        tst.set_stat2(index, '~{}'.format(bias_volt))
        tst.get_device(txt).set_stat1(cont_curr)
        tst.get_device(txt).set_stat2(bias_volt)
        print('switched at {} V with {} A'.format(bias_volt, cont_curr))
        tst.get_data().warn('switched at {} V with {} A'.format(bias_volt, cont_curr))
    
    #log.info('end backoff {}, {}'.format(bias_volt, cont_curr))
    tst.get_log().info('end backoff {}, {}'.format(bias_volt, cont_curr))
    
    # this to clear keithley screen
    bias_curr = bias_kt.read_curr()
    cont_curr = quick_read_curr(cont_kt, cont_volt)
    
  
if __name__ == '__main__':
    Nzero_Testing_AppApp().run()   
    bias_kt.set_curr(0)

 
# so that when ctrl+c, files will still close and voltage resets
try:
    #main()
    print "this part needs to be addressed. The integration."
    
except KeyboardInterrupt:
    bias_kt.set_volt(0)
    cont_kt.set_volt(0)
    print('closed with ctrl+c')
    log.info('closed with ctrl+c')
    hdlr1.close()
    hdlr2.close()
    sys.exit(0)
 
 
 
 
