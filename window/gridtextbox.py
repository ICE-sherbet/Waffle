import tkinter as tk
import re
class gridtextbox(tk.Text):
    def __init__(self,master,callBack = None,numLine = False):
        super().__init__(master)

        textX = 0
        textY = 0
        self.input_complete = True
        self.text = tk.Text(master,wrap='none',undo=True,width = 30,height=20)
        self.text.configure(font=("Courier", 14))
        self.isChange = False
        self.isNew = True
        x_sb = tk.Scrollbar(master,orient='horizontal')
        y_sb = tk.Scrollbar(master,orient='vertical',command=self.text.yview)
        
        if numLine:
            textX=1
            self.numberLine = TextLineNumbers(master,width=60,height = 2000, bg='#f0f0f0')
            self.numberLine.attach(self.text)
            self.numberLine.grid(column=0,row=0,sticky='ns')
            self.text.bind("<MouseWheel>", self.on_press_delay)
            y_sb.bind("<B1-Motion>", self.numberLine.redraw)
        # this is where we tell the custom widget what to call
        #self.text.set_callback(self.callback)
        
        self.text.grid(column=textX,row=textY,sticky="nsew")
        x_sb.config(command=self.text.xview)
        y_sb.config(command=self.text.yview)
        x_sb.grid(column=textX,row=textY+1,sticky='ew')
        y_sb.grid(column=textX+1,row=textY,sticky='ns')
        self.x_sb = x_sb
        self.y_sb = y_sb
        self.columnconfigure(0, weight=1)
        #self.hide_sb()
        if callBack is None:
            return
        self.callBack = callBack(self)
        self.text.bind("<KeyPress>",self.callBack.textboxPressCall)
        #self.text.bind("<Key>",self.callBack.textBoxKey)
        self.text.bind('<Return>', self.callBack.textBoxEnter)
        self.text.bind("<KeyRelease>",self.callBack.textboxReleaseCall)
        
    # スクロールバー非表示
    def hide_sb(self):
        self.x_sb.grid_forget()
        self.y_sb.grid_forget()

    # スクロールバー表示
    def show_sb(self):
        self.x_sb.grid_pack()
        self.y_sb.grid_pack()

    # フォントセット
    def setFont(self,size,weight,slant,underline,overstrike):
        self.text.configure(font=("Courier", 16, weight,slant,underline,overstrike))

    def set_state(self,_state):
        self.text.configure(state=_state)
    #テキストゲット
    def getText(self):
        return self.text.get("1.0",'end-1c')
    
    def on_press_delay(self, *args):
        self.after(2, self.numberLine.redraw)

class TextLineNumbers(tk.Canvas):
    """
    This is a Canvas widget to show Line numbers at along with Text widget
    """
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs, highlightthickness=0)
        self.textwidget = None
        self.repatter = re.compile('^\s*$')

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        line_number = int(str(i).split(".")[0])
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            linenum = str(i).split(".")[0]
            
            line_text= self.textwidget.get(str(i)+' linestart',str(i)+' lineend')
            i = self.textwidget.index("%s+1line" % i)
            if re.search('^\s*(;*|;+.*)$', line_text):
                continue
            y = dline[1]
            self.create_text(2, y, anchor="nw", text=str(line_number), fill="#606366",font=("Calibri",10))
            line_number += 1