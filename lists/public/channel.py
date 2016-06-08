﻿from source.data import argument
from source.public.channel import blockUrl
from source.public.channel import broadcaster
from source.public.channel import custom
from source.public.channel import feature
from source.public.channel import mod
from source.public.channel import owner
from source.public.channel import pyramid
from source.public.channel import reload
from source.public.channel import repeat
from source.public.channel import textformat
from source.public.channel import wall
from typing import Callable, List, Mapping, Optional

filterMessage = [
    blockUrl.filterNoUrlForBots
    ]  # type: List['argument.ChatCommand']

commands = {
    '!exit': owner.commandExit,
    '!managebot': owner.commandManageBot,
    '!reload': reload.commandReload,
    '!reloadcommands': reload.commandReloadCommands,
    '!reloadconfig': reload.commandReloadConfig,
    '!join': owner.commandJoin,
    '!part': owner.commandPart,
    '!emptychat': owner.commandEmpty,
    '!emptyall': owner.commandEmptyAll,
    '!global': custom.commandCommand,
    '!say': owner.commandSay,
    '!hello': broadcaster.commandHello,
    '!leave': broadcaster.commandLeave,
    '!feature': feature.commandFeature,
    '!empty': broadcaster.commandEmpty,
    '!autorepeat': repeat.commandAutoRepeat,
    '!pyramid': pyramid.commandPyramid,
    '!rpyramid': pyramid.commandRPyramid,
    '!wall': wall.commandWall,
    '!status': mod.commandStatus,
    '!title': mod.commandStatus,
    '!game': mod.commandGame,
    '!setgame': mod.commandRawGame,
    '!purge': mod.commandPurge,
    '!rekt': mod.commandPurge,
    '!command': custom.commandCommand,
    '!full': textformat.commandFull,
    '!parenthesized': textformat.commandParenthesized,
    '!circled': textformat.commandCircled,
    '!smallcaps': textformat.commandSmallCaps,
    '!upsidedown': textformat.commandUpsideDown,
    '!serifbold': textformat.commandSerifBold,
    '!serif-bold': textformat.commandSerifBold,
    '!serifitalic': textformat.commandSerifItalic,
    '!serif-italic': textformat.commandSerifItalic,
    '!serifbolditalic': textformat.commandSerifBoldItalic,
    '!serif-bolditalic': textformat.commandSerifBoldItalic,
    '!serifbold-italic': textformat.commandSerifBoldItalic,
    '!serif-bold-italic': textformat.commandSerifBoldItalic,
    '!serifitalicbold': textformat.commandSerifBoldItalic,
    '!serif-italicbold': textformat.commandSerifBoldItalic,
    '!serifitalic-bold': textformat.commandSerifBoldItalic,
    '!serif-italic-bold': textformat.commandSerifBoldItalic,
    '!sanserif': textformat.commandSanSerif,
    '!sanserifbold': textformat.commandSanSerifBold,
    '!sanserif-bold': textformat.commandSanSerifBold,
    '!bold': textformat.commandSanSerifBold,
    '!sanserifitalic': textformat.commandSanSerifItalic,
    '!sanserif-italic': textformat.commandSanSerifItalic,
    '!italic': textformat.commandSanSerifItalic,
    '!sanserifbolditalic': textformat.commandSanSerifBoldItalic,
    '!sanserif-bolditalic': textformat.commandSanSerifBoldItalic,
    '!sanserifbold-italic': textformat.commandSanSerifBoldItalic,
    '!sanserif-bold-italic': textformat.commandSanSerifBoldItalic,
    '!bolditalic': textformat.commandSanSerifBoldItalic,
    '!bold-italic': textformat.commandSanSerifBoldItalic,
    '!sanserifitalicbold': textformat.commandSanSerifBoldItalic,
    '!sanserif-italicbold': textformat.commandSanSerifBoldItalic,
    '!sanserifitalic-bold': textformat.commandSanSerifBoldItalic,
    '!sanserif-italic-bold': textformat.commandSanSerifBoldItalic,
    '!italicbold': textformat.commandSanSerifBoldItalic,
    '!italic-bold': textformat.commandSanSerifBoldItalic,
    '!script': textformat.commandScript,
    '!cursive': textformat.commandScript,
    '!scriptbold': textformat.commandScriptBold,
    '!cursivebold': textformat.commandScriptBold,
    '!script-bold': textformat.commandScriptBold,
    '!cursive-bold': textformat.commandScriptBold,
    '!fraktur': textformat.commandFraktur,
    '!frakturbold': textformat.commandFrakturBold,
    '!fraktur-bold': textformat.commandFrakturBold,
    '!monospace': textformat.commandMonospace,
    '!doublestruck': textformat.commandDoubleStruck,
    '!come': broadcaster.commandCome,
    '!autojoin': broadcaster.commandAutoJoin,
    '!uptime': broadcaster.commandUptime,
    }  # type: Mapping[str, Optional['argument.ChatCommand']]
commandsStartWith = {
    '!pyramid-': pyramid.commandPyramidLong,
    '!wall-': wall.commandWallLong,
    '!autorepeat-': repeat.commandAutoRepeat,
    '!settimeoutlevel-': broadcaster.commandSetTimeoutLevel,
    }  # type: Mapping[str, Optional['argument.ChatCommand']]

processNoCommand = [custom.customCommands]  # type: List['argument.ChatCommand']
