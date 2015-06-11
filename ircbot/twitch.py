﻿# Import some necessary libraries.
from config import config
import database.factory
import ircbot.irc
import threading
import traceback
import datetime
import sys
import time

print(str(datetime.datetime.now()) + ' Starting')
ircbot.irc.mainChat.start()
ircbot.irc.eventChat.start()
ircbot.irc.groupChat.start()
ircbot.irc.messaging.start()
ircbot.irc.join.start()

try:
    ircbot.irc.joinChannel(config.botnick, float('-inf'), ircbot.irc.mainChat)
    if config.owner:
        ircbot.irc.joinChannel(config.owner, float('-inf'),
                               ircbot.irc.mainChat)
    with database.factory.getDatabase() as db:
        for channelRow in db.getAutoJoinsChats():
            params = channelRow['broadcaster'], channelRow['priority'],
            if channelRow['eventServer']:
                params += ircbot.irc.eventChat,
            else:
                params += ircbot.irc.mainChat,
            ircbot.irc.joinChannel(*params)
    
    ircbot.irc.messaging.join()
except:
    ircbot.irc.messaging.running = False
    now = datetime.datetime.now()
    exc_type, exc_value, exc_traceback = sys.exc_info()
    _ = traceback.format_exception(*sys.exc_info())
    if config.exceptionLog is not None:
        with open(config.exceptionLog, 'a', encoding='utf-8') as file:
            file.write(now.strftime('%Y-%m-%d %H:%M:%S.%f '))
            file.write('Exception in thread ')
            file.write(threading.current_thread().name + ':\n')
            file.write(''.join(_))
    raise
finally:
    print(str(datetime.datetime.now()) + ' Ended')
