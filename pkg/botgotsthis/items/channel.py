﻿from typing import Iterable, Mapping, Optional

from lib import data
from ..channel import block_url
from ..channel import broadcaster
from ..channel import custom
from ..channel import feature
from ..channel import mod
from ..channel import owner
from ..channel import reload


def filterMessage() -> Iterable[data.ChatCommand]:
    yield block_url.filterNoUrlForBots


def commands() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!exit': owner.commandExit,
            '!managebot': owner.commandManageBot,
            '!reload': reload.commandReload,
            '!reloadcommands': reload.commandReloadCommands,
            '!reloadconfig': reload.commandReloadConfig,
            '!join': owner.commandJoin,
            '!part': owner.commandPart,
            '!emptychat': owner.commandEmpty,
            '!emptyall': owner.commandEmptyAll,
            '!global': custom.commandGlobal,
            '!say': owner.commandSay,
            '!hello': broadcaster.commandHello,
            '!leave': broadcaster.commandLeave,
            '!feature': feature.commandFeature,
            '!empty': broadcaster.commandEmpty,
            '!status': mod.commandStatus,
            '!title': mod.commandStatus,
            '!game': mod.commandGame,
            '!setgame': mod.commandRawGame,
            '!community': mod.commandCommunity,
            '!purge': mod.commandPurge,
            '!permit': mod.commandPermit,
            '!command': custom.commandCommand,
            '!come': broadcaster.commandCome,
            '!autojoin': broadcaster.commandAutoJoin,
            '!uptime': broadcaster.commandUptime,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.ChatCommand]]:
    if not hasattr(commandsStartWith, 'commands'):
        setattr(commandsStartWith, 'commands', {
            '!settimeoutlevel-': broadcaster.commandSetTimeoutLevel,
            })
    return getattr(commandsStartWith, 'commands')


def processNoCommand() -> Iterable[data.ChatCommand]:
    yield custom.customCommands