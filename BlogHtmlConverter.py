# -*- coding: utf-8 -*-

u"""
ブログの下書きをHTMLに変換する
"""


import sys
import codecs



"""
定数宣言
"""
UTF8_BOM = bytearray([0xEF, 0XBB, 0XBF])

KIND_NO_AREA = 0
KIND_DIV_AREA = 1
KIND_TALK_Q_AREA = 2
KIND_TALK_A_AREA = 3
KIND_LIST_1 = 4
KIND_AD_AREA = 5

MODE_LIST_1 = 1

"""
StrBlock型の変数にデータをセットする
ブロック要素
[div]
[talk_q]
[talk_a]
[list_1]
[ad]
"""
def BlockConvert(src_txt):

    count = 0
    startIndex = 0

    pack = []

    while count < 100: #100にしているのは無限ループ避けのため

        #次のブロックを取得する
        kind,getStr,nextIndex = GetBlockString(startIndex,src_txt)
        if(KIND_NO_AREA == kind):
            break

        startIndex = nextIndex;

        #print(getStr)
        #print('ほね')
        #print(nextIndex)
        #カウンターUP
        count += 1
        dict = {"kind": kind, "text": getStr}
        pack.append(dict)

    return pack



"""
    # 文字列を変換する
    index = src_txt.find('[div]')  # indexは1(2文字目)
    print(index)
    print len('[div]')

    index = src_txt.find('[/div]')  # indexは1(2文字目)
    print(index)  # 79

    # divの要素を取ってみる
    slice = src_txt[5:79]

    print slice
"""



"""
次のブロックの文字列を取得する
@:param 開始Index
@:param 元の文字列
@:returns 今回取得した種別,取得した文字列,次の位置
ブロック要素
[div]
[talk_q]
[talk_a]
[ad]
"""
def GetBlockString(startIndex, src_txt):

    minIndex = len(src_txt)
    nextIndex = 0
    kind = KIND_NO_AREA
    getStr = ""
    closeTagLen = 0

    #Divタグ
    index = src_txt.find('[div]',startIndex)
    if(index >= 0 and index < minIndex):
        minIndex = index

        kind = KIND_DIV_AREA

        nextIndex = src_txt.find('[/div]',minIndex)  # indexは1(2文字目)

        #print nextIndex

        # divの要素を取ってみる
        #-1している理由は、[/div]の前が改行コードのため
        getStr = src_txt[index+len('[div]') + 1:nextIndex-1]
        closeTagLen = len('[/div]')

    #talk_qタグ
    index = src_txt.find('[talk_q]', startIndex)
    if(index >= 0 and index < minIndex):
        minIndex = index

        kind = KIND_TALK_Q_AREA

        nextIndex = src_txt.find('[/talk_q]',minIndex)  # indexは1(2文字目)

        #print nextIndex

        # divの要素を取ってみる
        #-1している理由は、[/div]の前が改行コードのため
        getStr = src_txt[index+len('[talk_q]') + 1:nextIndex-1]
        closeTagLen = len('[/talk_q]')

    #talk_aタグ
    index = src_txt.find('[talk_a]', startIndex)
    if(index >= 0 and index < minIndex):
        minIndex = index

        kind = KIND_TALK_A_AREA
        
        nextIndex = src_txt.find('[/talk_a]',minIndex)  # indexは1(2文字目)

        #print nextIndex

        # divの要素を取ってみる
        #-1している理由は、[/div]の前が改行コードのため
        getStr = src_txt[index+len('[talk_a]') + 1:nextIndex-1]
        closeTagLen = len('[/talk_a]')

    #list_1タグ
    index = src_txt.find('[list_1]', startIndex)
    if(index >= 0 and index < minIndex):
        minIndex = index

        kind = KIND_LIST_1
        
        nextIndex = src_txt.find('[/list_1]',minIndex)  # indexは1(2文字目)

        #print nextIndex

        # list_1の要素を取ってみる
        #-1している理由は、[/list_1]の前が改行コードのため
        getStr = src_txt[index+len('[list_1]') + 1:nextIndex-1]
        closeTagLen = len('[/list_1]')

    return (kind,getStr,nextIndex+closeTagLen)


def ConvertHtml(blocks):

    outStr = ""
    for i in range(len(blocks)):
        block = blocks[i]
        str = ""
        if block['kind'] == KIND_DIV_AREA:
            #Divタグ用の処理
            str = TagDiv(block['text'])
        elif block['kind']  == KIND_TALK_Q_AREA:
            str = TagTalk(KIND_TALK_Q_AREA, block['text'])
        elif block['kind']  == KIND_TALK_A_AREA:
            str = TagTalk(KIND_TALK_A_AREA, block['text'])
        elif block['kind']  == KIND_LIST_1:
            str = TagList1(block['text'])            
        else:
            print u'該当する値はありません'

        outStr += str

    return outStr


def TagDiv(srcStr):

    #一行づつ取得
    srcStrs =  srcStr.split("\n")
    outStr = "<div>"

    mode = 0
    #一行ずつ処理する
    for i in range(len(srcStrs)):
        src =""

        if srcStrs[i].find('[list_1]') >= 0 :    #listか
            src = u'<ul class="hikage_list">' 
            mode = MODE_LIST_1

        elif srcStrs[i].find('[/list_1]') >= 0 :    #list終了か
            src = u'</ul>'
            mode = 0

        elif mode == MODE_LIST_1:
            src = '<li>'+ srcStrs[i] + '</li>'
            #リスト作成

        elif srcStrs[i].find('###') >= 0 :
            src = '<h3 class="hikage">' + srcStrs[i][3:] + '</h3>'
            src = '<p>' +src + '</p>'

        elif srcStrs[i].find('##') >= 0 :
            src = '<h2 class="hikage">' + srcStrs[i][2:] + '</h2>'
            src = '<p>' +src + '</p>'
        elif srcStrs[i].find('#') >= 0 :
            src = '<h1 class="hikage">' + srcStrs[i][1:] + '</h1>'
            src = '<p>' + src + '</p>'
        else:
            src = '<p>' + srcStrs[i] + '</p>'


        outStr += src

    outStr += '</div>'
    return outStr

def TagTalk(kind,srcStr):
    # 一行づつ取得
    srcStrs = srcStr.split("\n")
    outStr = ""

    #コメント部分の修正
    for i in range(len(srcStrs)):
        outStr += srcStrs[i] + '<br>'

    #会話文のタグ追加
    if(kind == KIND_TALK_Q_AREA):
        outStr = u'<div class="question_Box">'+u'<div class="question_image"><img src="http://xn--wimax-zv6jv79w.up.seesaa.net/image/question.jpg" alt="質問者の写真" width="90" height="90" /></div>'+'<div class="arrow_question">' + outStr +'</div></div>'
    else:
        outStr = u'<div class="question_Box">'+u'<div class="answer_image"><img src="http://xn--wimax-zv6jv79w.up.seesaa.net/image/answer.jpg" alt="回答者の写真" width="90" height="90" /></div>'+'<div class="arrow_answer">' + outStr +'</div></div>'



    return outStr

def TagAd(srcStr):
    outStr = ""

    #ファイルからAdリンクを取得
    f = codecs.open("adlink.txt",'r',"utf_8_sig")
    src_txt = f.read()
    f.close()

    outStr = src_txt

    return outStr

def TagList1(srcStr):
    # 一行づつ取得
    srcStrs = srcStr.split("\n")
    outStr = ""

    #コメント部分の修正
    for i in range(len(srcStrs)):
        outStr += '<li>'+ srcStrs[i] + '</li>'

    #uiの追加
    outStr = u'<ul class="hikage_list">' + outStr +'</ul>'

    return outStr

if __name__ == '__main__':
    # 変換の元ファイルを読み込む
    param = sys.argv
    if (len(param) == 0):
        print ("Usage: $ python " + param[0] + " number")
        quit()

    #UTF-8のBOMの考慮
    f = codecs.open(param[1],'r',"utf_8_sig")
    src_txt = f.read()
    f.close()


    #print(src_txt)
    blocks = BlockConvert(src_txt)


    #入力文字を分類する
    for i in range(len(blocks)):
        block = blocks[i]
        print("-----------------------------------------")
        print block

    #htmlに変換する
    output = ConvertHtml(blocks)

    print output
    f = codecs.open('blogOutput.txt', 'w',"utf_8_sig")  # 書き込みモードで開く
    f.write(output)  # シーケンスが引数。
    f.close()

