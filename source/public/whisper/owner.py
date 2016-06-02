﻿from ..library import channel, exit, managebot, send
from ..library.whisper import permission
from bot import globals, utils

@permission('owner')
def commandHello(args):
    utils.whisper(args.nick, 'Hello Kappa')
    return True

@permission('owner')
def commandExit(args):
    exit.botExit(send.whisper(args.nick))
    return True

@permission('owner')
def commandSay(args):
    if args.message.lower[1] in globals.channels:
        channel.botSay(args.database, args.nick, args.message.lower[1],
                       args.message[2:])
    return True

def commandJoin(args):
    if len(args.message) < 2:
        return False

    chan = args.message.lower[1]
    
    channel.botJoin(args.database, chan, send.whisper(args.nick))
    return True

def commandPart(args):
    if len(args.message) < 2:
        return False
    channel.botPart(args.message.lower[1], send.whisper(args.nick))
    return True

def commandEmptyAll(args):
    channel.botEmptyAll(send.whisper(args.nick))
    return True

def commandEmpty(args):
    if len(args.message) < 2:
        return False
    channel.botEmpty(args.message.lower[1], send.whisper(args.nick))
    return True

@permission('owner')
def commandManageBot(args):
    if len(args.message) < 2:
        return False
    
    return managebot.botManageBot(args.database, send.whisper(args.nick),
                                  args.nick, args.message)
