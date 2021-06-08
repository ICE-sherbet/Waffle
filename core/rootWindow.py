import tkinter as tk

from window.Window import Window
from enum import Enum, unique,auto
from icon.base64 import *

from core.menuData import MenuData
from core.buttonData import buttonData
from core.dictionalyKey import dictionaryWidgetKey
from core.TextBoxCall import waffleTextBoxCall
from core.ConfigRead import ConfigRead


dk = dictionaryWidgetKey
class rootWindow():
    def __init__(self):

        self.config_data = ConfigRead()
        

        #ウィンドウ作成
        self.CreateWindow()
        
        self.menu = MenuData(self.app)

        #アイコン設定
        self.setIcon()
        
        #ウィジェット作成
        #ボタンの作成
        self.create_button()
        #テキストボックス作成
        self.CreateTextBox()
        #フレーム作成
        #メニュー作成
        self.CreateMenu()

        #イベントの設定
        self.EventSet()

        self.app.mainloop()


    # ウィンドウを作成しやす
    def CreateWindow(self):
        self.rootWin = tk.Tk()
        self.app = Window(master=self.rootWin,appName = "わっふる",width = 1000,height=450,single_rootWindow = self)
        
    # アイコンを設定する
    def setIcon(self):#https://teratail.com/questions/175796 これのおかげ
        #self.rootWin.iconbitmap(default = 'waffle128.ico')
        self.rootWin.tk.call('wm', 'iconphoto', self.rootWin._w, tk.PhotoImage(data=appIcon))
        self.open_button_img = tk.PhotoImage(data=OPEN_BUTTON_ICON).subsample(3, 3)
        self.go_button_img = tk.PhotoImage(data=GO_BUTTON_ICON).subsample(3, 3)

        self.save_button_img = tk.PhotoImage(data=SAVE_BUTTON_ICON).subsample(3, 3)

    # テキストボックスを作成しやすぜ
    def CreateTextBox(self):
        self.app.mainFrame()
        self.app.textBoxCreate(dk.editerBox,waffleTextBoxCall,frame = self.app.main_frame,num_line = True)

    def create_frame(self,name):
        self.app.create_frame(dk.buttonFrame,tk.RAISED,2)

    def create_button(self):
        index = 0
        buttons = buttonData(self.app)
        for keybar , valbar in buttons._buttonDictinary_.items():
            self.app.create_frame(keybar,tk.RAISED,2)
            for dic,arr in valbar.items():
                self.app.create_button(dic, self.get_app_widget(keybar).frame 
                                       ,arr[0],dic.value,arr[1]
                                       ,index,0)
                index += 1
        #self.app.create_button(dk.buildButton,self.get_app_widget(dk.buttonFrame).frame,self.go_button_img,"実行")


    def get_app_widget(self,dic):
        return self.app.getWidgetDic(dic)

    #イベントを設定します
    def EventSet(self):
        
        dk = dictionaryWidgetKey
        menu_cmd = self.menu._menuDictinaly_
        self.get_app_widget(dk.editerBox).text.bind('<F5>',menu_cmd[dk.buildmenu][dk.build])

    # メニューを作成しやす
    def CreateMenu(self):
        self.app.menuRootCreate("menu")
        for keybar , valbar in self.menu._menuDictinaly_.items():
            self.app.menuBarPackCreate("menu",keybar,valbar)

