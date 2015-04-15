from config import config
import ircchannel.charConvert
import database.factory
import ircbot.irc
import datetime
import re

def customCommands(channelData, nick, originalMsg, msgParts, permissions):
    command = msgParts[0].lower()
    channel = channelData.channel[1:]
    message = None
    
    with database.factory.getDatabase() as db:
        commands = db.getChatCommands(channel, command)
        hasTextConvert = db.hasFeature(channelData.channel[1:], 'textconvert')
    
    permissionsSet = ['', 'turbo', 'subscriber', 'moderator', 'broadcaster',
                      'globalMod', 'admin', 'staff', 'owner',]
    for perm in permissionsSet:
        if not perm or permissions[perm]:
            if perm in commands['#global']:
                message = commands['#global'][perm]
            if perm in commands[channel]:
                message = commands[channel][perm]
    
    if message:
        currentTime = datetime.datetime.utcnow()
        cooldown = datetime.timedelta(seconds=config.customMessageCooldown)
        if (not permissions['moderator'] and
            'customCommand' in channelData.sessionData):
            since = currentTime - channelData.sessionData['customCommand']
            if since < cooldown:
                return
        channelData.sessionData['customCommand'] = currentTime

        cooldown = datetime.timedelta(seconds=config.customMessageUserCooldown)
        if 'customUserCommand' not in channelData.sessionData:
            channelData.sessionData['customUserCommand'] = {}
        if (not permissions['moderator'] and
            nick in channelData.sessionData['customUserCommand']):
            oldTime = channelData.sessionData['customUserCommand'][nick]
            since = currentTime - oldTime
            if since < cooldown:
                return
        channelData.sessionData['customUserCommand'][nick] = currentTime
        
        query = str(originalMsg.split(None, 1)[1]) if len(msgParts) > 1 else ''
        final = []
        try:
            for part in _parseFormatMessage(str(message)):
                plain, field, format, default, original = part
                final.append(plain)
                if field is not None:
                    string = _getString(str(field), str(default), originalMsg,
                                        msgParts, nick, query)
                    if string is not None:
                        string = _formatString(str(string), str(format),
                                               hasTextConvert)
                    else:
                        string = str(original)
                    final.append(str(string))
        except:
            final.append(str(message))
        channelData.sendMessage(''.join(final))

def commandCommand(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 3:
        return False
    
    r = parseCommandMessageInput(message)
    if r is None:
        return
    
    com, action, level, command, fullText = r
    broadcaster = channelData.channel[1:]
    if com == '!global':
        broadcaster = '#global'
    
    if level == False:
        channelData.sendMessage(nick + ' -> Invalid level, command ignored')
        return
    if level:
        if level not in permissions:
            channelData.sendMessage(
                nick + ' -> Invalid level, command ignored')
            return
        elif not permissions[level]:
            channelData.sendMessage(
                nick + ' -> You do not have permission to set that level')
            return
    
    if action in ['add', 'insert', 'new']:
        if not fullText:
            channelData.sendMessage(
                'You need to specify some text for that command')
            return
        
        with database.factory.getDatabase() as db:
            result = db.insertCustomCommand(
                broadcaster, level, command, fullText, nick)
            if result:
                channelData.sendMessage(command + ' was added successfully')
            else:
                channelData.sendMessage(
                    command + ' was not added successfully. There might be '
                    'an existing command')
    elif action in ['edit', 'update']:
        if not fullText:
            channelData.sendMessage(
                'You need to specify some text for that command')
            return
        
        with database.factory.getDatabase() as db:
            result = db.updateCustomCommand(
                broadcaster, level, command, fullText, nick)
            if result:
                channelData.sendMessage(
                    command + ' was updated successfully')
            else:
                channelData.sendMessage(
                    command + ' was not updated successfully. The command '
                    'might not exist')
    elif action in ['replace', 'override']:
        with database.factory.getDatabase() as db:
            result = db.replaceCustomCommand(
                broadcaster, level, command, fullText, nick)
            if result:
                channelData.sendMessage(
                    command + ' was updated successfully')
            else:
                channelData.sendMessage(
                    command + ' was not updated successfully. The command '
                    'might not exist')
    elif action in ['del', 'delete', 'rem', 'remove',]:
        with database.factory.getDatabase() as db:
            result = db.deleteCustomCommand(broadcaster, level, command, nick)
            if result:
                channelData.sendMessage(
                    command + ' was removed successfully')
            else:
                channelData.sendMessage(
                    command + ' was not removed successfully. The command '
                    'might not exist')

def parseCommandMessageInput(message):
    allowPermissions = {
        None: '',
        '': '',
        'any': '',
        'all': '',
        'public': '',
        'turbo': 'turbo',
        'twitchturbo': 'turbo',
        'subscriber': 'subscriber',
        'sub': 'subscriber',
        'moderator': 'moderator',
        'mod': 'moderator',
        'broadcaster': 'broadcaster',
        'streamer': 'broadcaster',
        'me': 'broadcaster',
        'globalMod': 'globalMod',
        'globalmod': 'globalMod',
        'global_mod': 'globalMod',
        'gmod': 'globalMod',
        'admin': 'admin',
        'twitchadmin': 'admin',
        'staff': 'staff',
        'twitchstaff': 'staff',
        'owner': 'owner',
        'self': 'owner',
        'bot': 'owner',
        }
    
    try:
        m = message
        originalCommand, action, m = m.split(None, 2)
        level = None
        if m.startswith('level='):
            parseLevel, m = m.split(None, 1)
            level = parseLevel[len('level='):]
        if level in allowPermissions:
            level = allowPermissions[level]
        else:
            level = False
        mparts = m.split(None, 1)
        while len(mparts) < 2:
            mparts.append(None)
        command, fullText = mparts
        
        return (originalCommand, action.lower(), level, command, fullText)
    except Exception:
        return None

def _parseFormatMessage(message):
    parsed = []
    i = 0
    length = len(message)
    
    while True:
        noFormat = []
        while i < length:
            char = message[i]
            i += 1
            
            if char == '}':
                if i < length and message[i] == '}':
                    i += 1
                else:
                    raise ValueError()
            elif char == '{':
                if i < length and message[i] == '{':
                    i += 1
                else:
                    i -= 1
                    break
            
            noFormat.append(char)
        
        if i == length:
            if noFormat:
                parsed.append((''.join(noFormat), None, None, None, None))
            break
        
        s = i
        i += 1
        if i == length:
            raise ValueError()
        
        field = []
        while True:
            if i == length:
                raise ValueError()
            
            char = message[i]
            i += 1
            
            if char == ':':
                break
            if char == '!':
                break
            if char == '{':
                if i < length and message[i] == '{':
                    i += 1
                else:
                    raise ValueError()
            if char == '}':
                if i < length and message[i] == '}':
                    i += 1
                else:
                    i -= 1
                    break
            field.append(char)

        format = []
        if char == ':':
            while True:
                if i == length:
                    raise ValueError()
                
                char = message[i]
                i += 1
                
                if char == '!':
                    break
                if char == '{':
                    if i < length and message[i] == '{':
                        i += 1
                    else:
                        raise ValueError()
                if char == '}':
                    if i < length and message[i] == '}':
                        i += 1
                    else:
                        i -= 1
                        break
                format.append(char)

        default = []
        if char == '!':
            while True:
                if i == length:
                    raise ValueError()
                
                char = message[i]
                i += 1
                
                if char == '{':
                    if i < length and message[i] == '{':
                        i += 1
                    else:
                        raise ValueError()
                if char == '}':
                    if i < length and message[i] == '}':
                        i += 1
                    else:
                        i -= 1
                        break
                default.append(char)

        if char != '}':
            raise ValueError()
        i += 1
        original = message[s:i]
        
        parsed.append((''.join(noFormat),
                       ''.join(field),
                       ''.join(format),
                       ''.join(default),
                       original))
        
    return parsed

def _getString(field, default, message, msgParts, nick, query):
    if field.lower() == 'user' or field.lower() == 'nick':
        return nick if nick else default
    
    if field.lower() == 'query':
        return query if query else default
    
    try:
        match = re.fullmatch(r'(\d+)(-(\d+))?|(\d+)-|-(\d+)', field)
        if match is not None:
            matchParts = match.groups()
            if matchParts[0] is not None:
                i = int(matchParts[0])
                if i >= len(msgParts):
                    return default
                if matchParts[2] is None:
                    return msgParts[i]
                else:
                    s = message.split(None, i)[i]
                    j = int(matchParts[2])
                    if len(msgParts) > j:
                        k = len(msgParts) - j - 1
                        return s.rsplit(None, k)[0]
                    else:
                        return s
            elif matchParts[3] is not None:
                i = int(matchParts[3])
                msgParts = message.split(None, i)
                if i < len(msgParts):
                    return msgParts[i]
                else:
                    return default
            elif matchParts[4] is not None:
                i = int(matchParts[4])
                if i == 0:
                    return msgParts[0]
                elif len(msgParts) >= 2:
                    if len(msgParts) <= i:
                        return message.split(None, 1)[1]
                    else:
                        k = len(msgParts) - i - 1
                        msg = message.rsplit(None, k)[0]
                        return msg.split(None, 1)[1]
                else:
                    return default
    except TypeError:
        return None

    return None

def _formatString(string, format, hasTextConvert):
    format = format.lower()
    if hasTextConvert:
        if format == 'ascii':
            return ircchannel.charConvert.allToAscii(string)
        if format == 'full':
            return ircchannel.charConvert.asciiToFullWidth(string)
        if format == 'parenthesized':
            return ircchannel.charConvert.asciiToParenthesized(string)
        if format == 'circled':
            return ircchannel.charConvert.asciiToCircled(string)
        if format == 'smallcaps':
            return ircchannel.charConvert.asciiToSmallCaps(string)
        if format == 'upsidedown':
            return ircchannel.charConvert.asciiToUpsideDown(string)
    return string
