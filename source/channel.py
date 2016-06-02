﻿from .database import factory
from bot import config, utils
from bot.channel import Channel
from bot.data.argument import ChatCommandArgs
from bot.data.message import Message
from bot.data.permissions import ChatPermissionSet
from lists import channel as commandList
import datetime
import sys
import threading
import time
import traceback

# Set up our commands function
def parse(chat, tags, nick, rawMessage, timestamp):
    if len(rawMessage) == 0:
        return
    
    message = Message(rawMessage)
    if len(message) == 0:
        return
    
    name = '{channel}-{command}-{time}'.format(
        channel=chat.channel, command=message.command, time=time.time())
    params = chat, tags, nick, message, timestamp
    threading.Thread(target=chatCommand, args=params, name=name).start()
    
def chatCommand(chat, tags, nick, message, timestamp):
    if False: # Hints for Intellisense
        chat = Channel('', None)
        nick = str()
        message = Message('')
    
    try:
        permissions = ChatPermissionSet(tags, nick, chat)
    
        with factory.getDatabase() as database:
            arguments = ChatCommandArgs(database, chat, tags, nick, message,
                                        permissions, timestamp)
            for command in commandsToProcess(message.command):
                if command(arguments):
                    return
    except:
        extra = 'Channel: {channel}\nMessage: {message}'.format(
            channel=chat.channel, message=message)
        utils.logException(extra, timestamp)

def commandsToProcess(command):
    yield from commandList.filterMessage
    if command in commandList.commands:
        if commandList.commands[command] is not None:
            yield commandList.commands[command]
    for starting in commandList.commandsStartWith:
        if command.startswith(starting):
            if commandList.commandsStartWith[starting] is not None:
                yield commandList.commandsStartWith[starting]
    yield from commandList.processNoCommand
