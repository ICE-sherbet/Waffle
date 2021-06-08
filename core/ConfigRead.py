import configparser
import os
import sys
from core.configmanager import *


class ConfigRead():
    def __init__(self):
        config = configparser.ConfigParser()
        config['SETTING'] = {
        'QuickPath': '.\\',
        'QuickInput': True
        }
        path = '.'
        name = '\\config.ini'
        if not os.path.isfile(path+name):
            with open(path+name, 'w') as file:
                config.write(file)
        ini = configparser.SafeConfigParser()
        
        INI_FILE = ".\\config.ini"
        q_path = '.\\'
        if os.path.exists(INI_FILE):
            ini.read(INI_FILE, encoding='utf8')
            self.q_path = show_key(ini,'SETTING','QuickPath','.\\')
            self.q_input = show_key_bool(ini,'SETTING','QuickInput',True)
