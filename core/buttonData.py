import tkinter as tk
from core.dictionalyKey import dictionaryWidgetKey
from core.menuCommand import menuCmd
from icon.base64 import *

class buttonData():
    

    
    def __init__(self,window):
        dk = dictionaryWidgetKey
        mc = menuCmd(window)
        
        self.open_button_img = OPEN_BUTTON_ICON
        self.go_button_img =   GO_BUTTON_ICON
        self.save_button_img = SAVE_BUTTON_ICON

        self._buttonDictinary_ = {
            dk.homeButtonFrame:{
                dk.buildButton: [self.go_button_img,mc.menubuild],
                dk.openButton: [self.open_button_img,mc.fileopen],
                dk.saveButton:[self.save_button_img,mc.save]
            }
    
        }
    