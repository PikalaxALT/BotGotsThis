﻿from ..common import timeout
from bot import config
import datetime

def commandWall(db, channel, nick, message, msgParts, permissions, now):
    if (not db.hasFeature(channel.channel, 'modwall') and
        not permissions['broadcaster']):
        return False
    
    if len(msgParts) < 2:
        return False
    rep = msgParts[1] + ' '
    if permissions['broadcaster']:
        length = 5
        rows = 20
    else:
        length = 3
        rows = 5
    try:
        if len(msgParts) == 3:
            rows = int(msgParts[2])
        else:
            length = int(msgParts[2])
            rows = int(msgParts[3])
    except:
        pass
    length = min(length, config.messageLimit // len(rep))
    if not permissions['broadcaster']:
        length = min(length, 5)
        rows = min(rows, 10)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modWall' in channel.sessionData:
            since = currentTime - channel.sessionData['modWall']
            if since < cooldown:
                return False
        channel.sessionData['modWall'] = currentTime
    elif not permissions['globalMod']:
        length = min(length, 20)
        rows = min(rows, 500)
    spacer = '' if permissions['channelModerator'] else ' \ufeff'
    messages = [rep * length + ('' if i % 2 == 0 else spacer)
                for i in range(rows)]
    channel.sendMulipleMessages(messages, 2)
    return True

def commandWallLong(db, channel, nick, message, msgParts, permissions, now):
    if (not db.hasFeature(channel.channel, 'modwall') and
        not permissions['broadcaster']):
        return False
    
    msgParts = message.split(None, 1)
    if len(msgParts) < 2:
        return False
    try:
        rows = int(msgParts[0].split('wall-')[1])
    except:
        if permissions['broadcaster']:
            rows = 20
        else:
            rows = 5
    if not permissions['broadcaster']:
        rows = min(rows, 10)
        
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.spamModeratorCooldown)
        if 'modWall' in channel.sessionData:
            since = currentTime - channel.sessionData['modWall']
            if since < cooldown:
                return False
        channel.sessionData['modWall'] = currentTime
    elif not permissions['globalMod']:
        rows = min(rows, 500)
    spacer = '' if permissions['channelModerator'] else ' \ufeff'
    messages = [msgParts[1] + ('' if i % 2 == 0 else spacer)
                for i in range(rows)]
    channel.sendMulipleMessages(messages, 2)
    if permissions['channelModerator']:
        timeout.recordTimeoutFromCommand(db, channel, nick, messages[0],
                                         message, 'wall')
    return True
