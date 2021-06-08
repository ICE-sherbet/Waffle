
import tkinter as tk

class Frame(tk.Frame):
    def __init__(self,master,_relief,_bd):
        self.master = master
        self.frame = tk.Frame(master,relief = _relief,bd = _bd)
        self.frame.grid(row=0,column=0,columnspan=2,sticky="nsew")