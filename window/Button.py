
import tkinter as tk

class Button(tk.Button):
    def __init__(self,master,cmd = None,icondata = None,text = None,x = 0,y = 0):
        self.master = master
        self.img = tk.PhotoImage(data=icondata).subsample(3, 3)
        self.button = tk.Button(master,text =text,image=self.img,compound="top",borderwidth=0,command = cmd)
        self.button.grid(row=y,column=x,sticky="ew",padx = 5 , pady = 5)

        #self.button.pack()



    def setText(self,_text):
        self.button.configure(text = _text)

    def setImage(self,ImageData):
        pass
