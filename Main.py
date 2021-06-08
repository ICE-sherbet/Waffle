import tkinter

from core.rootWindow import rootWindow


class MainClass:
    def Main(self):
        self.root = rootWindow()



if __name__ == '__main__':
    obj = MainClass()
    obj.Main()
