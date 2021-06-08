from command.MenuCommand import MenuCommand
from core.build import Build
from core.dictionalyKey import dictionaryWidgetKey as dk
import tkinter
import tkinter.ttk as ttk
from core.configmanager import *
from tkinter import filedialog
class menuCmd(MenuCommand):
    def __init__(self,window):
        self.window = window
        self.build = None
        self.isSetting = False
        self.isResult = False
        self.isNewSave = False
        self.isSave = False
        self.path = ""

    def menubuild(self,event = None):
        self.createResultFrame()
        self.build = Build(self.window)
        try:
            self.build.cmd()
        except:
            pass

    def topLabelsave(self):
        self.code_save()

    def newfile(self):
        if not self.window.getWidgetDic(dk.editerBox).isNew:
            if not self.isNewSave:
                self.newsave()
            if self.window.getWidgetDic(dk.editerBox).isChange:
                self.save()
        isNewSave = True
        self.window.getWidgetDic(dk.editerBox).isChange = False
        self.window.getWidgetDic(dk.editerBox).text.delete('1.0','end')


    def save(self):
        if not self.isNewSave:
            self.newsave()
            return
        allcode = ";*** [Let'S　CASLⅡ] ***\n"+self.window.getWidgetDic(dk.editerBox).getText()
        with open(self.path,'w',encoding="ansi") as f: 
            f.writelines(allcode)
        self.window.getWidgetDic(dk.editerBox).isChange = False

        #self.window.create_new_window(dk.setting,100,100)

    def fileopen(self):
        if not self.window.getWidgetDic(dk.editerBox).isNew:
            print("aa")
            if not self.isNewSave:
                self.newsave()
            if self.window.getWidgetDic(dk.editerBox).isChange:
                self.save()
        
        name = self.open_dialog([("CASL2",".cs2"),("テキスト",".txt")])
        if not name:
            return
        self.path = name
        self.window.getWidgetDic(dk.editerBox).isNew = True
        with open(name,'r',encoding="ansi") as f:
            self.window.getWidgetDic(dk.editerBox).text.delete('1.0','end')
            for line in f.readlines()[1:]:
                self.window.getWidgetDic(dk.editerBox).text.insert('end',line)

    def fileClose(self):
        self.window.windowClose()

    def newsave(self):
        allcode = ";*** [Let'S　CASLⅡ] ***\n"+self.window.getWidgetDic(dk.editerBox).getText()
        name = self.save_dialog([("CASL2",".cs2"),("テキスト",".txt")],"cs2")
        if not name:
            return
        
        self.isNewSave = True
        self.path = name
        with open(name,'w',encoding="ansi") as f: 
            f.writelines(allcode)
        self.window.getWidgetDic(dk.editerBox).isChange = False

    def code_save(self):
        allcode = ";*** [Let'S　CASLⅡ] ***\n"+self.window.getWidgetDic(dk.editerBox).getText()
        name = self.window.getWidgetDic(dk.editerBox).text.get("1.0 wordstart",'1.0 wordend')+".cs2"
        if name == '\n.cs2':
            name = "Default.cs2"
        path = self.window.rootWindow.config_data.q_path + '\\'
        print(name)
        self.path = path + name
        with open(path + name,'w',encoding="ansi") as f: 
            f.writelines(allcode)
        self.window.getWidgetDic(dk.editerBox).isChange = False

    def createResultFrame(self):
        if self.isResult:
            return
        self.isResult = True
        self.build_frame2 = ttk.Frame(self.window)
        self.build_frame2.grid(row=1, column=1,sticky="nsew", pady=1,padx=1)
        self.build_frame2.rowconfigure(0, minsize=0, weight=1)
        self.build_frame2.columnconfigure(0, minsize=0, weight=1)
        self.window.textBoxCreate(name = dk.editerResultBox,frame = self.build_frame2)
        #self.window.getWidgetDic(name = dk.editerResultBox).set_state('disabled')
        
        self.window.columnconfigure(1, minsize=600, weight=1)

    def close_setting_window(self):

        window = self.window.getWidgetDic(dk.setting)
        print("settingCLOSE")
        ini = configparser.SafeConfigParser()
        path = window.getWidgetDic(dk.pathEntry).get()
        iscom = window.getWidgetDic(dk.checkboxconfigd).get()
        INI_FILE = ".\\config.ini"
        if os.path.exists(INI_FILE):
            ini.read(INI_FILE, encoding='utf8')
            set_value(ini,'SETTING','QuickPath',path)
            set_value(ini,'SETTING','QuickInput',str(iscom))
            with open(INI_FILE, "w", encoding='utf8') as f:
                ini.write(f)
        else:
            print("ファイルがない")
        self.window.rootWindow.config_data.q_path = path
        self.window.rootWindow.config_data.q_input = iscom
        self.window.getWidgetDic(dk.editerBox).input_complete = iscom
        window.master.destroy()
        self.isSetting = False
        self.window.delWidgetDic(dk.setting)
        #with open(path+"\\test.txt", mode='w') as f:
        #    f.write("testtest")

    

    def menu_setting(self):

        if self.isSetting:
            return
        #
        config = configparser.ConfigParser()

        config['SETTING'] = {
        'QuickPath': '.\\'
        }
        path = '.'
        name = '\\config.ini'
        if not os.path.isfile(path+name):
            with open(path+name, 'w') as file:
                config.write(file)
        ini = configparser.SafeConfigParser()
        
        INI_FILE = ".\\config.ini"
        q_path = '.\\'
        q_path = True
        if os.path.exists(INI_FILE):
            ini.read(INI_FILE, encoding='utf8')
            q_path = show_key(ini,'SETTING','QuickPath', '.\\')
            q_input = show_key_bool(ini,'SETTING','QuickInput', True)
        

        self.isSetting = True
        self.window.create_new_window(dk.setting,500,200,self.close_setting_window,False)
        setting_window = self.window.getWidgetDic(dk.setting)
        setting_window.create_label_place(dk.pathlabel,10,100)
        setting_window.create_entry_place(dk.pathEntry,140,100,20)
        setting_window.create_checkbutton_place(dk.checkboxconfig,10,80)
        window = self.window.getWidgetDic(dk.setting)

        window.getWidgetDic(dk.pathEntry).insert(tkinter.END,q_path)
        window.getWidgetDic(dk.checkboxconfigd).set(q_input)

        