﻿import configparser
import os.path
import json
import os

mainServer = 'irc.twitch.tv'
eventServer = '199.9.252.26'
ini = configparser.ConfigParser()
ini.read('config.ini')
botnick = str(ini['BOT']['botnick']).lower()
password = str(ini['BOT']['password'])
owner = str(ini['BOT']['owner']).lower()

modLimit = min(int(ini['BOT']['modLimit']), 100)
modSpamLimit = min(int(ini['BOT']['modSpamLimit']), 100)
publicLimit = min(int(ini['BOT']['publicLimit']), 20)
publicDelay = float(ini['BOT']['publicDelay'])
messagePerSecond = float(ini['BOT']['messagePerSecond'])
messagePerSecond = messagePerSecond if messagePerSecond > 0 else 20

joinLimit = min(int(ini['BOT']['joinLimit']), 50)
joinPerSecond = float(ini['BOT']['joinPerSecond'])
joinPerSecond = joinPerSecond if joinPerSecond > 0 else 20

ircLogFolder = str(ini['BOT']['ircLogFolder'])
exceptionLog = str(ini['BOT']['exceptionLog'])
if ircLogFolder and not os.path.isdir(ircLogFolder):
    os.mkdir(ircLogFolder)
