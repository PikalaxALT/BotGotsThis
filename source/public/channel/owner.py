﻿from bot import config, globals
from ..common import channel, exit, managebot, send
import datetime
import json
import sys
import time

def commandExit(db, chanObj, nick, message, msgParts, permissions):
    exit.botExit(send.channel(chanObj))
    return True

def commandSay(db, chanObj, nick, message, msgParts, permissions):
    msgParts = message.split(None, 2)
    msgParts[1] = msgParts[1].lower()
    if msgParts[1] in globals.channels:
        channel.botSay(msgParts[1], msgParts[2])
    return True

def commandJoin(db, chanObj, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False

    chan = msgParts[1].lower()
    channel.botJoin(db, chan, send.channel(chanObj))
    return True

def commandPart(db, chanObj, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    channel.botPart(chan, send.channel(chanObj))
    return True

def commandEmptyAll(db, chanObj, nick, message, msgParts, permissions):
    channel.botEmptyAll(send.channel(chanObj))
    return True

def commandEmpty(db, chanObj, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    channel.botEmpty(msgParts[1], send.channel(chanObj))
    return True

def commandManageBot(db, chanObj, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    
    return managebot.botManageBot(db, send.channel(chanObj),
                                  nick, message, msgParts)
