
from CallBack.absTextBoxCall import absTextBoxCall
from core.waffleTable import *
from tkinter import *
from tkinter import ttk

class waffleTextBoxCall(absTextBoxCall):
    
    def __init__(self,gridText):
        self.textbox = gridText
        self.isChange = False
        re_label = "(?P<label>[A-Za-z_][A-Za-z0-9_]*)?"
        re_op = "\s+(?P<op>[A-Z]+)"
        re_arg =">=?(([-#]?[A-Za-z0-9_]+)|(\'.*\')))"
        re_arg0 = "(?P<arg0" + re_arg
        re_arg1 = "(?P<arg1" + re_arg
        re_arg2 = "(?P<arg2" + re_arg
        re_args = "(\s+%s(\s*,\s*%s(\s*,\s*%s)?)?)?" % (re_arg0, re_arg1, re_arg2)
        re_comment = "(\s*(;(?P<comment>.+)?)?)?"
        self.tokenPattern = re.compile("(^" + re_label + re_op + re_args + ")?" + re_comment)
        self.is_completion_decision = False
        self.str_completion_decision = ""
        self.labels = {}

    def textboxPressCall(self,event):
        return
        if not event.char:
            return
        print(self.textbox.isNew)
        token = self.textbox.text.get("insert -1c wordstart",'insert -1c wordend')
        if token == '\n':
            token = ''
        intext = token + event.char

        self.completionList = [s for s in OP_TOKEN if s.startswith(intext)]


            
        if len(self.completionList)==1:
            self.isChange = True

    def tokenSplit(self,line):
        result = re.match(self.tokenPattern, line)
        label = result.group('label')
        op = result.group('op')
        args = []

        for i in range(3):
            if result.group('arg'+str(i)):
                args.append(result.group('arg'+str(i)))
            else:
                args = None if i==0 else args
                break
        return Instruction(label, op, args, 0, line)

    def textBoxEnter(self,event):
        print("enter")

    def completion(self):
        if not self.textbox.input_complete:
            print("change-RETURN")
            return
        print("change")
        self.textbox.text.delete("insert -1c wordstart",'insert -1c wordend')
        self.textbox.text.insert('insert',self.completionList[0])


    def textBoxKey(self,event):
        pass

    def textboxReleaseCall(self,event):
        
        self.textbox.isChange = True
        self.textbox.isNew = False
        index = self.textbox.text.index('insert linestart')
        line = self.textbox.text.get("insert linestart",'insert lineend')
        token = self.textbox.text.get("insert -1c wordstart",'insert -1c wordend')
        self.textbox .numberLine.redraw()
        self.completionList = []
        self.completion_op_List = []
        self.completion_arg_List = []
        labels = {}
        i = self.textbox.text.index("@0,0")
        while True :
            dline= self.textbox.text.dlineinfo(i)
            if dline is None: break
            linenum = str(i).split(".")[0]
            inst = self.tokenSplit(self.textbox.text.get(str(i)+' linestart',str(i)+' lineend'))
            i = self.textbox.text.index("%s+1line" % i)
            if not inst.label is None:
                labels[i] = inst.label
        inst = self.tokenSplit(line)
            
        if not inst.op is None and not inst.op in OP_TOKEN:
            self.completion_op_List = [s for s in OP_TOKEN if s.startswith(inst.op)]
        if not inst.args is None:
            if len(inst.args)>1 and not inst.args[1] in labels.values():
                self.completion_arg_List = [s for s in labels.values() if s.startswith(inst.args[1])]
        self.completionList = self.completion_op_List + self.completion_arg_List
        
            
        if len(self.completionList)==1 and not event.keysym=='BackSpace':
            self.str_completion_decision = token
            self.completion()
            self.is_completion_decision = True
class Instruction:
    def __init__(self, label, op, args, linenumber,line):
        self.label = label
        if not op is None:
            self.op = op.upper()
        else:
            self.op = op
        self.args = args
        self.linenumber = linenumber
        self.src = line
    
    #printとか文字列で、出力するとき
    def __str__(self):
        return '%d: %s, %s, %s' % (self.linenumber, self.label, self.op, self.args)
