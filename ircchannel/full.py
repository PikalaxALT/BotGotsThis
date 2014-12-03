﻿import ircbot.irc

normal = (''' !"#$%&'()*+,-./'''
          '0123456789'
          ':;<=>?@'
          'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
          '[\\]^_`'
          'abcdefghijklmnopqrstuvwxyz'
          '{|}~')
wide = ('''　！＂＃＄％＆＇（）＊＋，ー．／'''
        '０１２３４５６７８９'
        '：；〈＝〉？＠'
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        '［＼］＾＿｀'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        '｛｜｝～')

def commandFull(channelData, nick, message, msgParts, permissions):
    msg = message.split(None, 1)[1]
    fullMsg = []
    for i in range(len(msg)):
        j = normal.find(msg[i])
        if j != -1:
            fullMsg.append(wide[j])
        else:
            fullMsg.append(msg[i])
    return channelData.sendMessage(''.join(fullMsg))
