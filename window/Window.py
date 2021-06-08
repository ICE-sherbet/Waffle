
import tkinter
import tkinter.ttk as ttk
from window.gridtextbox import gridtextbox
from window.Menu import Menu
from window.Frame import Frame
from window.Button import Button
from tkinter import filedialog

class Window(tkinter.Frame):
    #初期化
    def __init__(self,master,appName,width,height,rootwindow = True,single_rootWindow=None,rsize = True):
        super().__init__(master)
        #self.event_check()
        self.master = master
        self.rootWindow = single_rootWindow
        self.textBoxList = []
        self.textBoxDictionary = {}
        self.widgetDictionary = {}
        self.name = appName
        self.resize(width,height,rsize)
        if not rootwindow:
            return
        self.nameChange(appName)
        self.grid(column=0,row=0,sticky=tkinter.NSEW)
        self.master.minsize(320,400)
        #列の引き伸ばし
        #self.rowconfigure(0, weight=1)
        #行の引き伸ばし
        #self.columnconfigure(0, weight=1)
        
        self.master.rowconfigure(0, minsize=0, weight=1)
        self.master.columnconfigure(0, minsize=0, weight=1)
        self.rowconfigure(1, minsize=0, weight=1)
        self.columnconfigure(0, minsize=380, weight=1)

    def create_new_window(self,name,width,height,callBack = None,rsize = True):
        self.widgetDictionary[name.value] = Window(tkinter.Toplevel(self.master),name,width,height,False,self.rootWindow,rsize)
        print(name.value)
        if callable is None:
            return
        self.widgetDictionary[name.value].master.protocol("WM_DELETE_WINDOW", callBack)
    def mainFrame(self):
        self.main_frame = tkinter.Frame(self)
        self.main_frame.grid(row=1, column=0,sticky="nsew", pady=1,padx=1)
        
        self.main_frame.rowconfigure(0, minsize=0, weight=1)
        self.main_frame.columnconfigure(0, minsize=60, weight=0)
        self.main_frame.columnconfigure(1, minsize=300, weight=1)
        self.main_frame.columnconfigure(2, minsize=20, weight=0)
        self.build_frame = tkinter.Frame(self)
        self.build_frame.grid(row=1, column=0,sticky="nsew", pady=1,padx=1)
        
        self.now_frame = self.main_frame
        self.now_frame.tkraise()

    #大きさ変更
    def resize(self,width,height,rsize = True):
        self.height = height
        self.width = width
        self.master.geometry(str(self.width)+'x'+str(self.height))
        self.master.resizable(height=rsize, width=rsize)

    #名前変える
    def nameChange(self,appName):
        self.name = appName
        self.master.title(self.name)

    #テキストボックス作成
    def textBoxCreate(self,name,callBack = None,frame = None,num_line = False):
        if frame is None:
            frame = self
        # tkinter.Label(frame, text='Oh My God!', bg='red', relief=tkinter.RIDGE, bd=2).grid(row=1, column=1,sticky="nsew", pady=1,padx=1)

        self.widgetDictionary[name.value] = gridtextbox(frame,callBack,num_line)
    
    #テキストを返す
    def getText(self,name):
        return self.widgetDictionary[name.value].getText()
    #フレームを作成
    def create_frame(self,name,_relief,_bd):
        self.widgetDictionary[name.value] = Frame(self,_relief,_bd)

    #ボタンを作成
    def create_button(self,name,root = None,icondata = None,text = None,cmd = None,x=0,y=0):
        if root is None:
            root = self
        self.widgetDictionary[name.value] = Button(root,cmd
                                                   ,icondata,text
                                                   ,x,y)

    #メニューを作成
    def menuRootCreate(self,name):
        self.widgetDictionary[name] = Menu(self.master)
    #メニューバーの作成
    def menuBarPackCreate(self,root,parent,child):
        self.widgetDictionary[root].addMenu(parent)
        for key , val in child.items():
            self.widgetDictionary[root].addCommand(parent,key.value,val)
        self.widgetDictionary[root].packMenyu(parent.value,parent)

    #ラベルを作成
    def create_label_place(self,name,x,y):
        self.widgetDictionary[name.value] = tkinter.Label(self.master,text=name.value)
        self.widgetDictionary[name.value].place(x=x,y=y)
    #チェックボックスを作成
    def create_checkbutton_place(self,name,x,y):
        self.widgetDictionary[name.value+"d"] = tkinter.BooleanVar()
        self.widgetDictionary[name.value+"d"].set(True)
        self.widgetDictionary[name.value] = tkinter.Checkbutton(self.master,variable = self.widgetDictionary[name.value+"d"],text=name.value)
        self.widgetDictionary[name.value].place(x=x,y=y)
    #入力ボックス作成
    def create_entry_place(self,name,x,y,width=100):
        self.widgetDictionary[name.value] = tkinter.Entry(self.master,width=width)
        self.widgetDictionary[name.value].place(x=x,y=y)

    def getWidgetDic(self,name):
        return self.widgetDictionary[name.value]
    def delWidgetDic(self,name):
        del self.widgetDictionary[name.value]
    #ウィンドウを閉じる
    def windowClose(self):
        self.master.destroy()
        #print("fileOpen")
    
    def event_check(self):
        # 利用可能なイベントを全てbind
        for event_type in tkinter.EventType.__members__.keys():
            event_seq= "<" + event_type + ">"
            try:
                self.master.bind_all(event_seq, self.event_handler)
                #print(event_type)
            except tkinter.TclError:
                #print("bind error:", event_type)
                pass
    # イベントハンドラ
    def event_handler(self,event):
        print(event.type)