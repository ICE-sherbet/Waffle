from core.dictionalyKey import dictionaryWidgetKey
from core.menuCommand import menuCmd

class MenuData():
    

    
    def __init__(self,window):
        dk = dictionaryWidgetKey
        mc = menuCmd(window)
        
        self._menuDictinaly_ = {
            dk.filemenu : {
                dk.newfile: mc.newfile,
                dk.open: mc.fileopen,
                dk.close:mc.fileClose,
                dk.save:mc.save,
                dk.newsave:mc.newsave,
                dk.topLabelsave:mc.topLabelsave,
                dk.setting:mc.menu_setting
            },
            #dk.editmenu : {
            #    dk.undo : mc.undo
            #},
            dk.buildmenu : {
                dk.build : mc.menubuild
            }
    
        }
    