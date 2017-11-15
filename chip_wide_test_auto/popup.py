"""
Date: 2017/07/19
Written by: Hyun Kyo Jung
Description: Module for communicating with the tester when he inserts wrong info.
"""

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

def give_warning(msg):
    """warns the tester to insert the correct information to the textinput field"""
    content = Button(text = 'close me!')
    popup = Popup(content = content, title = msg, auto_dismiss = False)
    content.bind(on_press = popup.dismiss)
    popup.open()



