from core.waffleTable import *
from core.math import *
from core.dictionalyKey import dictionaryWidgetKey as dk
import re

import contextlib
import operator
import sys, os, string, array
import time
class Build:
    
    class Error(BaseException):
        def __init__(self, line_num, src, message):
            self.line_num = line_num
            self.src = src
            self.message = message

        def report(self):
            print >> sys.stderr, "Error: %s\nLine %d: %s" % (self.message, self.line_num, self.src)

    def __init__(self,window):
        self.window = window
        self.result_box = window.getWidgetDic(name = dk.editerResultBox)
        
        self.repatter = re.compile('^\s*$')

        re_label = "(?P<label>[A-Za-z_][A-Za-z0-9_]*)?"
        re_op = "\s+(?P<op>[A-Z]+)"
        re_arg =">=?(([-#]?[A-Za-z0-9_]+)|(\'.*\')))"
        re_arg0 = "(?P<arg0" + re_arg
        re_arg1 = "(?P<arg1" + re_arg
        re_arg2 = "(?P<arg2" + re_arg
        re_args = "(\s+%s(\s*,\s*%s(\s*,\s*%s)?)?)?" % (re_arg0, re_arg1, re_arg2)
        re_comment = "(\s*(;(?P<comment>.+)?)?)?"
        self.tokenPattern = re.compile("(^" + re_label + re_op + re_args + ")?" + re_comment)
        
        #仮
        self.filename = "test"
        self.addr = 0
        start_offset = 0
        self.label_count = 0
        
        self.tmp_code = []
        self._symbols = {}
        
        self.additional_dc = []


        self.gen_code_func = [self.gen_code_noarg, self.gen_code_r, self.gen_code_r1r2,
                              self.gen_code_adrx, self.gen_code_radrx,
                              self.gen_code_ds, self.gen_code_dc, self.gen_code_strlen,
                              self.gen_code_start]

        self.start_found = False
    def print_mem(self,mem):
        width = 8
        print(mem)
        print(len(mem))
        try:
            for i in range(0, len(mem), width):
                line = " ".join([f"{m.value:04x}" for m in mem[i:i+width]])
                print(f"# [{i:04x}]: {line}")
        except TypeError as e:
            return True
        print("")
        return False

    def cmd(self):
        #self.text = self.window.getText(dk.editerBox)
        self.texts = self.window.getWidgetDic(dk.editerBox).text.get("1.0", "end-1c").splitlines()
        self.currentNumber = 0
        #空白行はあらかじめカットして命令用のクラスを作る
        tokens = [self.tokenSplit(i,line) for i,line in enumerate(self.texts) if not self.repatter.match(line)]
        [print(s) for s in tokens]
        self._mem = []
        #[self._mem.extend([Element(i.code[0], i.linenumber),Element(i.code[1], i.linenumber+1)]) for i in self.parse(tokens)[1:-1] if i is not None]
        try:
            for i in self.parse(tokens)[1:]:
                print("code:")
                print(i)
                [self._mem.append(Element(code, i.linenumber)) for code in i.code]
        except TypeError as e:
            print("エラーのため実行不可")
            return

        if self.print_mem(self._mem):
            print("エラーのため実行不可")
            return
        end = len(self._mem)
        start = time.time()

        c = Comet2(self._mem,window = self.window)
        grlist = [0,0,0,0,0,0,0,0]
        c.init_regs(grlist, 0)
        with contextlib.ExitStack() as stack:
            print("end"+str(end))
            c.run(0, end)
        elapsed_time = time.time() - start
        print(elapsed_time)

    def parse(self,tokens):
        if tokens[0].op != "START":
            return

        for index,line in enumerate(tokens):
            if self.parse_line(index,line):
                print("エラーのため終了")
                return
                # ラベルをアドレスに置換。
        
        code_list = [self.replace_label(code) for code in self.tmp_code if code != None]
        # =記法のリテラル用コードを末尾に加える。
        code_list.extend(self.additional_dc)


##         print >> sys.stderr, '-- Second pass --'
##         for i in code_list:
##             print >> sys.stderr, i

        return code_list
        # =記法のリテラル用コードを生成する
    def gen_additional_dc(self, x, n):
        l = self.gen_label()
        label_name = '.' + l
        self._symbols[label_name] = Label(label_name, n, self.filename, self.addr)
        const = self.cast_literal(x[1:])
        code = array.array('H', const)
        self.addr += len(code)
        # self.additional_dc.append((code, n, '%s\tDC\t%s' % (l,x[1:])))
        self.additional_dc.append(ByteCode(code, self._symbols[label_name].addr, n, '%s\tDC\t%s' % (l,x[1:])))
        return self._symbols[label_name].addr
    
    # ラベルの文字列を生成する
    def gen_label(self):
        l = '_L' + '%04d' % self.label_count
        self.label_count += 1
        return l

    def replace_label(self, bcode):
        ''' ラベルをアドレスに置換 '''
        def conv(x, bcode):
            if type(x) == type('str'):
                if x[0] == '=':
                    return self.gen_additional_dc(x, bcode.linenumber)
                #
                global_name = x
                if x in self._symbols.keys():
                    return self._symbols[x].addr
                #
                # スコープ内にないときは、スコープ名なしのラベルを探す
                elif global_name in self._symbols.keys():
                    if self._symbols[global_name].goto == '':
                        return self._symbols[global_name].addr
                    # サブルーチンの実行開始番地が指定されていた場合、gotoに書かれているラベルの番地にする
                    else:
                        label = self._symbols[global_name].goto
                        if label in self._symbols.keys():
                            return self._symbols[label].addr
                        else:
                            pass
                        #
                    #
                else:
                    pass
                    #raise self.Error(bcode.linenumber, bcode.src, 'Undefined label "%s" was found.' % x.split('.')[1])
            else:
                return x

        return ByteCode([conv(i, bcode) for i in bcode.code], bcode.addr, bcode.linenumber, bcode.src)


    def parse_line(self,index,inst):
        label = inst.label
        if label is not None:
            self.add_label(index,inst)#label追加
        op = inst.op
        if op is  None:
            return True
        if not op in OP_TOKEN:
            return True
        if op == "OUT":
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," PUSH 0,GR1")))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," PUSH 0,GR2")))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," LAD GR1,"+inst.args[0])))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," LAD GR2,"+inst.args[1])))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," SVC 2")))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," POP GR2")))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," POP GR1")))
            return False
        if op == "IN":
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," PUSH 0,GR1")))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," PUSH 0,GR2")))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," LAD GR1,"+inst.args[0])))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," LAD GR2,"+inst.args[1])))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," SVC 1")))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," POP GR2")))
            self.tmp_code.append(self.convert(index,self.tokenSplit(index," POP GR1")))
            return False
        elif op == "RPUSH":
            if len(args) != 0:
                self.err_exit(f"bad args (L{self._line_num})")
            [self.tmp_code.append(self.convert(index,self.tokenSplit(index," PUSH "+reg))) for reg in reg_str]
            return False
        elif op == "RPOP":
            if len(args) != 0:
                self.err_exit(f"bad args (L{self._line_num})")
            [self.tmp_code.append(self.convert(index,self.tokenSplit(index," POP "+reg))) for reg in reg_str]
            return False
        self.tmp_code.append(self.convert(index,inst))
        
        return False
        

    def convert(self,index,inst):
        if -100 < OP_TABLE[inst.op][0] < 0:
            if self.is_gr(inst.args[1]):
                inst.op += '1'
            else:
                inst.op += '2'

        if OP_TABLE[inst.op][0] == -100:#START_OP
            if self.start_found:
                # サブルーチンの実行開始番地が指定されていた場合、gotoに実行開始番地をセットする
                if inst.args != None:
                    self._symbols[inst.label].goto = self.conv_adr(inst.args[0])
                return None
            else:
                self.start_found = True
                return ByteCode(self.gen_code_start(inst.op, inst.args), self.addr, inst.linenumber, inst.src)
        elif OP_TABLE[inst.op][0] == -101:
            self.current_scope = ''
            return None
        elif OP_TABLE[inst.op][0] < 0:
            return None
        
        bcode = ByteCode(self.gen_code_func[OP_TABLE[inst.op][1]](inst.op, inst.args), self.addr, inst.linenumber, inst.src)
        self.addr += len(bcode.code)
        
        print(bcode)
        return bcode


    #GRが判定
    def is_gr(self,arg):
        if arg[0:2] == 'GR':
            return True
        else:
            return False


    def add_label(self, index,inst):
        label = inst.label
        if label in self._symbols:
            pass#後に修正(エラー処理)
        self._symbols[label] = Label(label, index, self.filename, self.addr)

    # 字句解析
    def tokenSplit(self,index,line):
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
        return Instruction(label, op, args, index, line)





    
    def conv_noarg(self, args):
        return (None,)

    def conv_r(self, args):
        return (reg_str[args[0]], )

    def conv_r1r2(self, args):
        return (reg_str[args[0]], reg_str[args[1]])

    def conv_adrx(self, args):
        addr = self.conv_adr(args[0])
        if len(args) == 1:
            return (addr, 0)
        return (addr, reg_str[args[1]])

    def conv_radrx(self, args):
        addr = self.conv_adr(args[1])
        if len(args) == 2:
            return (reg_str[args[0]], addr, 0)
        return (reg_str[args[0]], addr, reg_str[args[2]])

    def conv_adr(self, addr):
        if re.match('-?[0-9]+', addr) != None:
            a = s2u(int(addr))
        elif re.match('#[A-Za-z0-9]+', addr) != None:
            a = int(addr[1:], 16)
        elif re.match('[A-Za-z_][A-Za-z0-9_]*', addr) != None:
            a = addr
        elif re.match('=.+', addr) != None:
            a = addr
            print("conv_adr-loteral:"+addr)
        return a



    def gen_code_noarg(self, op, args):
        code = [0]
        code[0] = (OP_TABLE[op][0] << 8)
        return code

    def gen_code_r(self, op, args):
        code = [0]
        code[0] = ((OP_TABLE[op][0] << 8) | (self.conv_r(args)[0] << 4))
        return code

    def gen_code_r1r2(self, op, args):
        code = [0]
        r1, r2 = self.conv_r1r2(args)
        code[0] = ((OP_TABLE[op][0] << 8) | (r1 << 4) | r2)
        return code

    def gen_code_adrx(self, op, args):
        code = [0, None]
        addr, x = self.conv_adrx(args)
        code[0] = ((OP_TABLE[op][0] << 8) | (0 << 4) | x)
        code[1] = addr
        return code

    def gen_code_radrx(self, op, args):
        code = [0, None]
        r, addr, x = self.conv_radrx(args)
        code[0] = ((OP_TABLE[op][0] << 8) | (r << 4) | x)
        code[1] = addr
        return code

    def gen_code_ds(self, op, args):
        code = array.array('H', [0]*int(args[0]))
        return code

    def gen_code_dc(self, op, args):
        const = self.cast_literal(args[0])
        code = array.array('H', const)
        return code

    # IN,OUT用
    def gen_code_strlen(self, op, args):
        print("IN OUT")
        code = [0, None, None]
        code[0] = (OP_TABLE[op][0] << 8)
        code[1] = self.conv_adr(args[0])
        code[2] = self.conv_adr(args[1])
        return code

    # START用
    def gen_code_start(self, op, args):
        code = [0]*8
        code[0] = (ord('C') << 8) + ord('A')
        code[1] = (ord('S') << 8) + ord('L')
        if args != None:
            addr, x = self.conv_adrx(args)
            code[2] = addr
        return code
    
    def cast_literal(self, arg):
        if arg[0] == '#':
            value = [int(arg[1:], 16)]
        elif arg[0] == '\'':
            value = [ord(i) for i in arg[1:-1]]
        else:
            value = [s2u(int(arg))]
        return value

class Element:
    """
    メモリの1要素分のデータ構造
    """
    def __init__(self, v, l, vlabel=None, label=None):
        # int この要素の値
        self.value = v
        # int (debug用) asmでの行番号を格納する asmと無関係または値が実行時に書き換えられた場合は0
        self.line = l
        # str (debug用) 値がラベル由来の場合のラベル名 それ以外はNone 値が実行時に書き換えられた場合はNone
        self.vlabel = vlabel
        # str (debug用) ラベルが指定された番地の場合のラベル名 それ以外はNone 実行時に変更されない
        self.label = label

class Label:    
    def __init__(self, label, lines=0, filename='', addr=0, goto=''):
        self.label = label
        self.lines = lines
        self.filename = filename
        self.addr = addr
        self.goto = goto

    def __str__(self):
        scope, label = self.label.split('.')
        if len(scope) == 0:
            s = '%s:%d\t%04x\t%s' % (self.filename, self.lines, self.addr, label)
        else:
            s = '%s:%d\t%04x\t%s (%s)' % (self.filename, self.lines, self.addr, label, scope)
        return s
class Instruction:
    def __init__(self, label, op, args, linenumber,line):
        self.label = label
        self.op = op.upper()
        self.args = args
        self.linenumber = linenumber
        self.src = line
    
    #printとか文字列で、出力するとき
    def __str__(self):
        return '%d: %s, %s, %s' % (self.linenumber, self.label, self.op, self.args)

class ByteCode:
    def __init__(self, code, addr, linenumber, src):
        self.code = code
        self.addr = addr
        self.linenumber = linenumber
        self.src = src

    def __str__(self):
        try:
            s = '%04x\t%04x\t\t%d\t%s' % (self.addr, self.code[0], self.linenumber, self.src)
        except IndexError:
            s = '%04x\t    \t\t%d\t%s' % (self.addr, self.linenumber, self.src)
        if 1 < len(self.code):
            s += '\n'
            try:
                s += '%04x\t%04x' % (self.addr+1, self.code[1])
            except TypeError:
                s += '%04x\t%s' % (self.addr+1, self.code[1])
        if 2 < len(self.code):
            s += '\n'
            try:
                s += '%04x\t%04x' % (self.addr+2, self.code[2])
            except TypeError:
                s += '%04x\t%s' % (self.addr+2, self.code[2])
        return s
class Element:
    """
    メモリの1要素分のデータ構造
    """
    def __init__(self, v, l, vlabel=None, label=None):
        # int この要素の値
        self.value = v
        # int (debug用) asmでの行番号を格納する asmと無関係または値が実行時に書き換えられた場合は0
        self.line = l
        # str (debug用) 値がラベル由来の場合のラベル名 それ以外はNone 値が実行時に書き換えられた場合はNone
        self.vlabel = vlabel
        # str (debug用) ラベルが指定された番地の場合のラベル名 それ以外はNone 実行時に変更されない
        self.label = label
# End Element

class Comet2:
    ADR_MAX = 0xffff
    REG_NUM = 8
    REG_BITS = 16
    SVC_OP_IN = 1
    SVC_OP_OUT = 2

    def __init__(self, mem, print_regs=True, simple_output=True,window = None):
        self.window = window
        self.result_box = window.getWidgetDic(name = dk.editerResultBox)
        self._print_regs = print_regs
        self._simple_output = simple_output

        self._gr = [0] * Comet2.REG_NUM

        self._pr = 0
        self._sp = 0

        self._zf = 0
        self._sf = 0
        self._of = 0

        self._call_level = 0
        self._fin = None
        self._fout = None
        self._fdbg = None
        self._input_all = None
        self.init_mem(mem)

        #log_output
        self.reg_log = [] #汎用レジスタ
        self.ea_log = [] #EA
        self.sp_log = [] #スタックポインタ
        self.fr_log = [] #OF,SF,ZF


        self.OP_TABLE = {
                0x00:self.op_NOP,
                0x10:self.op_LD, 0x11:self.op_ST, 0x12:self.op_LAD,
                0x14:self.op_LD_REG,
                0x20:self.op_ADDA, 0x21:self.op_SUBA, 0x22:self.op_ADDL,
                0x23:self.op_SUBL, 0x24:self.op_ADDA_REG,
                0x25:self.op_SUBA_REG, 0x26:self.op_ADDL_REG,
                0x27:self.op_SUBL_REG,
                0x30:self.op_AND, 0x31:self.op_OR, 0x32:self.op_XOR,
                0x34:self.op_AND_REG, 0x35:self.op_OR_REG,
                0x36:self.op_XOR_REG,
                0x40:self.op_CPA, 0x41:self.op_CPL, 0x44:self.op_CPA_REG,
                0x45:self.op_CPL_REG,
                0x50:self.op_SLA, 0x51:self.op_SRA, 0x52:self.op_SLL,
                0x53:self.op_SRL,
                0x61:self.op_JMI, 0x62:self.op_JNZ, 0x63:self.op_JZE,
                0x64:self.op_JUMP, 0x65:self.op_JPL, 0x66:self.op_JOV,
                0x70:self.op_PUSH, 0x71:self.op_POP,
                0x80:self.op_CALL, 0x81:self.op_RET,
                0xf0:self.op_SVC,
                0x91:self.op_SVC_OUT}

    def init_mem(self, mem):
        self._mem = mem
        len_mem = len(self._mem)
        len_max = Comet2.ADR_MAX + 1
        if len_mem == len_max:
            return
        if len_mem > len_max:
            self.err_exit("memory over")
        else:
            self._mem.extend([Element(0, 0) for _ in range(len_max - len_mem)])

    def init_regs(self, grlist=[0,0,0,0,0,0,0,0], pr=0, sp=0, zf=0, sf=0, of=0):
        if len(grlist) != Comet2.REG_NUM:
            self.err_exit("internal error grlist")
        self._gr = [gr&0xffff for gr in grlist]
        self._pr = pr & 0xffff
        self._sp = sp & 0xffff
        self._zf = int(zf != 0)
        self._sf = int(sf != 0)
        self._of = int(of != 0)

    def get_allmem(self):
        return self._mem

    def run(self, start, end, fout=None, fdbg=None, fin=None, virtual_call=False, input_all=False):
        self.result_box.text.delete("1.0","end")
        self._fout = fout
        self._fdbg = fdbg
        self._fin = fin
        self._pr = start & 0xffff
        end = end & 0xffff
        self.end = end
        self._input_all = input_all
        self.output_regs()
        if virtual_call:
            self._sp = (self._sp - 1) & 0xffff
            self._mem[self._sp].value = end
            if self._fdbg is not None:
                self._fdbg.write("VCALL: [----] " +
                        f"MEM[{self._sp:04x}] <- {end:04x} (SP <- {self._sp:04x})\n")
        while self._pr != end:
            self.run_once()
            self.reg_log.append(self._gr)
            self.sp_log.append(self._sp)
            self.fr_log.append(self._of << 2 | self._sf << 1 | self._zf) #OF,SF,ZF
        self.output_regs_textbox()
        print(self.reg_log)
        print(self.sp_log)
        print(self.fr_log)

    def run_once(self):
        self._inst_adr = self._pr
        elem = self.fetch()
        op = (elem.value & 0xff00) >> 8
        if op not in self.OP_TABLE:
            lstr = "" if elem.line == 0 else f"L{elem.line} "
            self.err_exit(f"unknown operation ({lstr}[{self._pr - 1:04x}]: {elem.value:04x})")
            
        self.OP_TABLE[op](elem)

    def err_exit(self, msg):
        print(f"Runtime Error: {msg}", file=sys.stderr)
        self.output_regs()
        sys.exit(1)

    def output_debug(self, elem, msg, print_flags=True):
        if not self._simple_output:
            return
        lstr = "--:" if elem.line == 0 else f"L{elem.line+1}:"
        flags = f"\n (ZF <- {self._zf}, SF <- {self._sf}, OF <- {self._of})" if print_flags else ""
        label = self._mem[self._inst_adr].label
        labelmsg = ""
        if label is not None:
            labelmsg = f"'{label}'="
        print(f"{lstr:>6} [{labelmsg}{self._inst_adr:04x}] {msg}{flags}\n")
        self.result_box.text.insert('end', f"{lstr:>6} [{labelmsg}{self._inst_adr:04x}] {msg}{flags}\n")
        self.output_regs()

    def output(self, msg):
        self.result_box.text.insert('end', f"OUT: {msg}\n")
        if self._simple_output:
            print(msg)
        else:
            self._fout.write(f"  OUT: {msg}\n")

    def output_regs(self):
        if not self._print_regs:
            return
        print("end")
        grlist = " ".join([f"GR{i}={gr:04x}" for i, gr in enumerate(self._gr)])
        print(f"\n-REGS: {grlist}\n")
        print(f"-REGS: PR={self._pr:04x} SP={self._sp:04x} ")
        print(f"ZF={self._zf} SF={self._sf} OF={self._of}\n\n")

    def output_regs_textbox(self):
        print("output_regs_textbox")
        grlist = " ".join([f"GR{i}={gr:04x}" for i, gr in enumerate(self._gr)])
        self.result_box.text.insert('end',f"\n  END: {grlist}\n")
        self.result_box.text.insert('end',f"  END: PR={self._pr:04x} SP={self._sp:04x} ")
        self.result_box.text.insert('end',f"ZF={self._zf} SF={self._sf} OF={self._of}\n\n")
        print("output_regs_textbox-end")

    def get_gr(self, n):
        if n < 0 or Comet2.REG_NUM <= n:
            self.err_exit("GR index out of range")
        return self._gr[n]

    def set_gr(self, n, val):
        if n < 0 or Comet2.REG_NUM <= n:
            self.err_exit("GR index out of range")
        self._gr[n] = val & 0xffff

    def get_mem(self, adr):
        if adr < 0 or Comet2.ADR_MAX < adr:
            self.err_exit("MEM address out of range")
        return self._mem[adr].value

    def set_mem(self, adr, val):
        if adr < 0 or Comet2.ADR_MAX < adr:
            self.err_exit("MEM address out of range")
        self._mem[adr].value = val & 0xffff
        self._mem[adr].line = 0
        self._mem[adr].vlabel = None

    def fetch(self):
        m = self._mem[self._pr&0xffff]
        self._pr = (self._pr + 1) & 0xffff
        
        return m

    @staticmethod
    def decode_1word(code):
        return ((code&0xff00)>>8, (code&0x00f0)>>4, (code&0x000f))

    @staticmethod
    def decode_2word(code1, code2):
        return ((code1&0xff00)>>8, (code1&0x00f0)>>4, code2, (code1&0x000f))

    def get_reg_adr(self, elem):
        code1 = elem.value
        elem2 = self.fetch()
        code2 = elem2.value
        _, opr1, opr2, opr3 = Comet2.decode_2word(code1, code2)
        if opr3 == 0:
            adr = opr2
            if elem2.vlabel is not None:
                adr_str = f"'{elem2.vlabel}'={adr:04x}"
            else:
                adr_str = f"{adr:04x}"
        else:
            offset = self.get_gr(opr3)
            adr = opr2 + offset
            if elem2.vlabel is None:
                adr_str = f"{adr:04x} <{opr2:04x} + GR{opr3}={offset:04x}>"
            else:
                adr_str = f"{adr:04x} <'{elem2.vlabel}'={opr2:04x} + GR{opr3}={offset:04x}>"
        adr = opr2 if opr3 == 0 else opr2 + self.get_gr(opr3)
        return (opr1, adr&0xffff, adr_str)

    def op_NOP(self, elem):
        self.output_debug(elem, "NOP", False)

    def op_LD(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        val = self.get_mem(adr)
        self._zf = int(val == 0)
        self._sf = (val&0x8000) >> 15
        self._of = 0
        self.set_gr(reg, val)
        self.output_debug(elem, f"GR{reg} <- MEM[{adr_str}]({val:04x})")

    def op_ST(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        val = self.get_gr(reg)
        self.set_mem(adr, val)
        self.output_debug(elem, f"MEM[{adr_str}] <- GR{reg}({val:04x})", False)

    def op_LAD(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        self.set_gr(reg, adr)
        self.output_debug(elem, f"GR{reg} <- {adr_str}", False)

    def op_LD_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        val = self.get_gr(reg2)
        self._zf = int(val == 0)
        self._sf = (val&0x8000) >> 15
        self._of = 0
        self.set_gr(reg1, val)
        self.output_debug(elem, f"GR{reg1} <- GR{reg2}({val:04x})")

    def add_flag(self, v1, v2, arithmetic=True):
        r = v1 + v2
        self._zf = int(r == 0)
        if arithmetic:
            sr = r & 0x8000
            sv1 = v1 & 0x8000
            sv2 = v2 & 0x8000
            self._sf = sr >> 15
            self._of = ((~(sv1 ^ sv2)) & (sv1 ^ sr)) >> 15
        else:
            self._sf = 0
            self._of = int(r > 0xffff)
        return r & 0xffff

    def sub_flag(self, v1, v2, arithmetic=True):
        r = v1 - v2
        self._zf = int(r == 0)
        if arithmetic:
            sr = r & 0x8000
            sv1 = v1 & 0x8000
            sv2 = v2 & 0x8000
            self._sf = sr >> 15
            self._of = ((sv1 ^ sv2) & (sv1 ^ sr)) >> 15
        else:
            self._sf = 0
            self._of = int(v1 < v2)
        return r & 0xffff

    def op_ADDA(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        r = self.add_flag(v1, v2)
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) + MEM[{adr_str}]({v2:04x})>")

    def op_SUBA(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        r = self.sub_flag(v1, v2)
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) - MEM[{adr_str}]({v2:04x})>")

    def op_ADDL(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        r = self.add_flag(v1, v2, False)
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) +L MEM[{adr_str}]({v2:04x})>")

    def op_SUBL(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        r = self.sub_flag(v1, v2, False)
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) -L MEM[{adr_str}]({v2:04x})>")

    def op_ADDA_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        r = self.add_flag(v1, v2)
        self.set_gr(reg1, r)
        self.output_debug(elem, f"GR{reg1} <- {r:04x} <GR{reg1}({v1:04x}) + GR{reg2}({v2:04x})>")

    def op_SUBA_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        r = self.sub_flag(v1, v2)
        self.set_gr(reg1, r)
        self.output_debug(elem, f"GR{reg1} <- {r:04x} <GR{reg1}({v1:04x})- GR{reg2}({v2:04x})>")

    def op_ADDL_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        r = self.add_flag(v1, v2, False)
        self.set_gr(reg1, r)
        self.output_debug(elem, f"GR{reg1} <- {r:04x} <GR{reg1}({v2:04x}) +L GR{reg2}({v2:04x})>")

    def op_SUBL_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        r = self.sub_flag(v1, v2, False)
        self.set_gr(reg1, r)
        self.output_debug(elem, f"[GR{reg1} <- {r:04x} <GR{reg1}({v1:04x}) -L GR{reg2}({v2:04x})> ")

    def bit_flag(self, op, v1, v2):
        r = op(v1, v2)
        self._zf = int(r == 0)
        self._sf = 0
        self._of = 0
        return r & 0xffff

    def op_AND(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        r = self.bit_flag(operator.and_, v1, v2)
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) & MEM[{adr_str}]({v2:04x})>")

    def op_OR(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        r = self.bit_flag(operator.or_, v1, v2)
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) | MEM[{adr_str}]({v2:04x})>")

    def op_XOR(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        r = self.bit_flag(operator.xor, v1, v2)
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) ^ MEM[{adr_str}]({v2:04x})>")

    def op_AND_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        r = self.bit_flag(operator.and_, v1, v2)
        self.set_gr(reg1, r)
        self.output_debug(elem, f"GR{reg1} <- {r:04x} <GR{reg1}({v1:04x}) & GR{reg2}({v2:04x})>")

    def op_OR_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        r = self.bit_flag(operator.or_, v1, v2)
        self.set_gr(reg1, r)
        self.output_debug(elem, f"GR{reg1} <- {r:04x} <GR{reg1}({v1:04x}) | GR{reg2}({v2:04x})>")

    def op_XOR_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        r = self.bit_flag(operator.xor, v1, v2)
        self.set_gr(reg1, r)
        self.output_debug(elem, f"GR{reg1} <- {r:04x} <GR{reg1}({v1:04x}) ^ GR{reg2}({v2:04x})>")

    @staticmethod
    def expand_bit(v):
        return v if (v & 0x8000) == 0 else -1 * (((~v) + 1) & 0xffff)

    def cmp_flag(self, v1, v2, arithmetic=True):
        self._of = 0
        if v1 == v2:
            self._zf = 1
            self._sf = 0
            return
        self._zf = 0
        if arithmetic:
            self._sf = int(Comet2.expand_bit(v1) < Comet2.expand_bit(v2))
        else:
            self._sf = int(v1 < v2)

    def op_CPA(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        self.cmp_flag(v1, v2)
        self.output_debug(elem, f"<GR{reg}({v1:04x}) - MEM[{adr_str}]({v2:04x})>")

    def op_CPL(self, elem):
        reg, adr, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        v2 = self.get_mem(adr)
        self.cmp_flag(v1, v2, False)
        self.output_debug(elem, f"<GR{reg}({v1:04x}) -L MEM[{adr_str}]({v2:04x})>")

    def op_CPA_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        self.cmp_flag(v1, v2)
        self.output_debug(elem, f"<GR{reg1}({v1:04x}) - GR{reg2}({v2:04x})>")

    def op_CPL_REG(self, elem):
        _, reg1, reg2 = Comet2.decode_1word(elem.value)
        v1 = self.get_gr(reg1)
        v2 = self.get_gr(reg2)
        self.cmp_flag(v1, v2, False)
        self.output_debug(elem, f"<GR{reg1}({v1:04x}) -L GR{reg2}({v2:04x})>")

    def op_SLA(self, elem):
        reg, v2, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        shift = v2 if v2 < self.REG_BITS else self.REG_BITS
        r = v1
        for _ in range(shift):
            self._of = (r & 0x4000) >> 14
            r = (((r << 1) & 0x7fff) | (v1 & 0x8000))
        self._zf = int(r == 0)
        self._sf = (v1 & 0x8000) >> 15
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) << {adr_str}>")

    def op_SRA(self, elem):
        reg, v2, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        shift = v2 if v2 < self.REG_BITS else self.REG_BITS
        r = v1
        for _ in range(shift):
            self._of = r & 0x0001
            r = (((r >> 1) & 0x7fff) | (v1 & 0x8000))
        self._zf = int(r == 0)
        self._sf = (v1 & 0x8000) >> 15
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) >> {adr_str}>")

    def op_SLL(self, elem):
        reg, v2, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        shift = v2 if v2 < self.REG_BITS + 1 else self.REG_BITS + 1
        r = v1
        for _ in range(shift):
            self._of = (r & 0x8000) >> 15
            r = (r << 1) & 0xffff
        self._zf = int(r == 0)
        self._sf = (r & 0x8000) >> 15
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) <<L {adr_str}>")

    def op_SRL(self, elem):
        reg, v2, adr_str = self.get_reg_adr(elem)
        v1 = self.get_gr(reg)
        shift = v2 if v2 < self.REG_BITS + 1 else self.REG_BITS + 1
        r = v1
        for _ in range(shift):
            self._of = r & 0x0001
            r = r >> 1
        self._zf = int(r == 0)
        self._sf = 0
        self.set_gr(reg, r)
        self.output_debug(elem, f"GR{reg} <- {r:04x} <GR{reg}({v1:04x}) >>L {adr_str}>")

    def op_JMI(self, elem):
        _, adr, adr_str = self.get_reg_adr(elem)
        msg = ""
        if self._sf != 0:
            self._pr = adr
            msg = f"PR <- {adr_str} "
        self.output_debug(elem, msg + "<if SF == 1>", False)

    def op_JNZ(self, elem):
        _, adr, adr_str = self.get_reg_adr(elem)
        msg = ""
        if self._zf == 0:
            self._pr = adr
            msg = f"PR <- {adr_str} "
        self.output_debug(elem, msg + "<if ZF == 0>", False)

    def op_JZE(self, elem):
        _, adr, adr_str = self.get_reg_adr(elem)
        msg = ""
        if self._zf != 0:
            self._pr = adr
            msg = f"PR <- {adr_str} "
        self.output_debug(elem, msg + "<if ZF == 1>", False)

    def op_JUMP(self, elem):
        _, adr, adr_str = self.get_reg_adr(elem)
        self._pr = adr
        self.output_debug(elem, f"PR <- {adr_str}", False)

    def op_JPL(self, elem):
        _, adr, adr_str = self.get_reg_adr(elem)
        msg = ""
        if self._sf == 0 and self._zf == 0:
            self._pr = adr
            msg = f"PR <- {adr_str} "
        self.output_debug(elem, msg + "<if SF == 0 and ZF == 0>", False)

    def op_JOV(self, elem):
        _, adr, adr_str = self.get_reg_adr(elem)
        msg = ""
        if self._of != 0:
            self._pr = adr
            msg = f"PR <- {adr_str} "
        self.output_debug(elem, msg + "<if OF == 1>", False)

    def op_PUSH(self, elem):
        _, adr, adr_str = self.get_reg_adr(elem)
        self._sp = (self._sp - 1) & 0xffff
        self.set_mem(self._sp, adr)
        self.output_debug(elem,
                f"MEM[SP={self._sp:04x}] <- {adr_str} (SP <- {self._sp:04x})", False)

    def op_POP(self, elem):
        _, reg, _ = Comet2.decode_1word(elem.value)
        adr = self._sp
        val = self.get_mem(adr)
        self.set_gr(reg, val)
        self._sp = (self._sp + 1) & 0xffff
        self.output_debug(elem,
                f"GR{reg} <- {val:04x} <MEM[SP={adr:04x}]> (SP <- {self._sp:04x})", False)

    def op_CALL(self, elem):
        self._call_level+=1;
        _, adr, adr_str = self.get_reg_adr(elem)
        self._sp = (self._sp - 1) & 0xffff
        val = self._pr
        self.set_mem(self._sp, val)
        self._pr = adr
        self.output_debug(elem,
                f"PR <- {adr_str}, MEM[SP={self._sp:04x}] <- PR={val:04x} " +
                f"(SP <- {self._sp:04x})", False)

    def op_RET(self, elem):
        self._pr = self.get_mem(self._sp)
        self._sp = (self._sp + 1) & 0xffff
        if self._call_level == 0:
            self._pr = self.end
            return
        self._call_level -=1
        self.output_debug(elem, f"PR <- {self._pr:04x} (SP <- {self._sp:04x})", False)

    def op_SVC(self, elem):
        code2 = self.fetch().value
        if code2 == Comet2.SVC_OP_IN:
            self.op_SVC_IN(elem)
        elif code2 == Comet2.SVC_OP_OUT:
            self.op_SVC_OUT(elem)
        else:
            self.err_exit(f"unknown SVC op 'SVC {code2:04x}'")

    def op_SVC_IN(self, elem):
        # IN: GR1(保存先アドレス) GR2(サイズ格納先アドレス)
        # self._finがNoneの場合、サイズ0の入力とみなす
        start = self.get_gr(1)
        self.output_debug(elem, "SVC IN", False)
        size = 0
        for _ in range(256):
            save_adr = (start + size) & Comet2.ADR_MAX
            instr = ""
            if self._fin is not None:
                while True:
                    instr = self._fin.read(1)
                    if instr == "" or self._input_all or Comet2.is_printable(instr):
                        break
            if instr == "":
                break
            d = ord(instr)&0xff
            self.set_mem(save_adr, d)
            self.output_debug(elem, f"IN: MEM[{save_adr:04x}] <- {d:04x} <input>", False)
            size += 1
        size_adr = self.get_gr(2)
        self.set_mem(size_adr, size)
        self.output_debug(elem, f"IN: MEM[{size_adr:04x}] <- {size:04x} <input size>", False)

    @staticmethod
    def is_printable(s):
        # JIS X 0201での印字可能文字
        c = ord(s)
        return (0x21 <= c and c <= 0x7e) or (0xa1 <= c and c <= 0xdf)

    def op_SVC_OUT(self, elem):
        # OUT: GR1(出力元アドレス) GR2(サイズ格納先アドレス)
        msg = []
        start = self.get_gr(1)
        end = start + self.get_mem(self.get_gr(2))
        adr = start
        for adr in range(start, end):
            adr = adr & Comet2.ADR_MAX
            msg.append(self.get_mem(adr)&0xff)
        self.output_debug(elem, f"SVC OUT MEM[{start:04x}]...MEM[{adr:04x}]", False)
        self.output(Comet2.to_str(msg))

    @staticmethod
    def to_str(ilist):
        # TODO ASCIIのみ (本来対応する文字コードはJIS X 0201)
        return "".join([chr(i) for i in ilist])
# End Comet2