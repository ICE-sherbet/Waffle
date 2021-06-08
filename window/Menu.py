import tkinter as tk
from tkinter import filedialog

class Menu(tk.Menu):
    def __init__(self,master):
        self.master = master
        self.menubar = tk.Menu(master)
        self.MenuDictionary = {}
        master.config(menu=self.menubar)

    #メニュー追加
    def addMenu(self,menuName):
        self.MenuDictionary[menuName] = tk.Menu(self.menubar, tearoff = 0)

    #メニューのコマンドの追加
    def addCommand(self,menuName,commandlabel,action):
        self.MenuDictionary[menuName].add_command(label = commandlabel,command = action)

    #メニューのコマンドの追加
    def addCommands(self,menuName,commands):
        for key , val in commands.items():
            self.MenuDictionary[menuName].add_command(label = key.value,command = val)

    #メニューの表示を決定
    def packMenyu(self,menuName,parent):
        self.menubar.add_cascade(label=menuName,menu = self.MenuDictionary[parent])
