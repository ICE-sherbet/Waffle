import configparser
import os
import sys


def show_config(ini):
    '''
    設定ファイルの全ての内容を表示する（コメントを除く）
    '''
    for section in ini.sections():
        print ("[" + section + "]")
        show_section(ini, section)
    return


def show_section(ini, section):
    '''
    設定ファイルの特定のセクションの内容を表示する
    '''
    for key in ini.options(section):
        show_key(ini, section, key)
    return


def show_key(ini, section, key,key2):
    '''
    設定ファイルの特定セクションの特定のキー項目（プロパティ）の内容を表示する
    '''
    if not ini.has_section(section):
        ini.add_section(section)
    cof = ini[section]
    print (section + "." + key + " = " + cof.get(key,'.\\'))
    return cof.get(key,key2)
def show_key_bool(ini, section, key,key2=True):
    '''
    設定ファイルの特定セクションの特定のキー項目（プロパティ）の内容を表示する
    '''
    if not ini.has_section(section):
        ini.add_section(section)
    cof = ini[section]
    return cof.getboolean(key,fallback=key2)

def set_value(ini, section, key, value):
    '''
    設定ファイルの特定セクションの特定のキー項目（プロパティ）の内容を変更する
    '''
    if not ini.has_section(section):
        ini.add_section(section)
    
    ini.set(section,key, value)
    print (section + "." + key + " = " + ini.get(section, key))
    return


def usage():
    sys.stderr.write("Usage: " + sys.argv[0] + " inifile [section [key [value]]]\n")
    return
