from tkinter import filedialog
import os

class MenuCommand:
    def fileopen(self):
        print("fileOpen")

    def fileClose(self):
        print("fileClose")

    def newfile(self):
        print("newfile")

    def save(self):
        print("Save")

    def newsave(self):
        print("newSave")
        
    def save_dialog(self,type,defalt):
        return filedialog.asksaveasfilename(
            title = "なまえをつけて保存",
            filetype = type,
            initialdir = "./",
            defaultextension = defalt
            )
    def open_dialog(self,type):
        iDir = os.path.abspath(os.path.dirname(__file__))
        return filedialog.askopenfilename(filetypes=type, initialdir=iDir)
    def topLabelsave(self):
        print("topLabelsave")

    def undo(self):
        print("undo")

    def menubuild(self):
        print("build")

    def menu_setting(self):
        print("setting")
