from enum import Enum, unique
@unique
class dictionaryWidgetKey(Enum):
    filemenu = "ふぁいる"
    newfile = "あたらしく"
    open = "ひらく"
    close = "とじる"
    save = "うわがきほぞん"
    newsave = "べつめいでほぞん"
    topLabelsave = "らべるで保存"
    setting = "せってい"

    editmenu = "へんしゅう"
    undo = "もとにもどす"

    buildmenu = "びるど"
    build = "このファイルをビルド"

    editerBox = "editerBox"
    editerResultBox = "editerResultBox"
    buttonFrame = "buttonFrame"

    pathEntry = "pathEntry"
    checkboxconfig = "入力補完"
    checkboxconfigd = "入力補完d"

    homeButtonFrame = "homeButtonFrame"
    buildButton = "実行(F5)"
    openButton = "開く"
    saveButton = "保存"
    quickSaveButton = "ラベルで保存"


    pathlabel = "クイック保存パス"
