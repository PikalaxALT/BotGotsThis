from ..data.message import Message
from ..data.permissions import ChatPermissionSet, WhisperPermissionSet
from ..database.databasebase import DatabaseBase
from bot.twitchmessage.irctags import IrcMessageTagsReadOnly
from datetime import datetime
from typing import Any, Callable, Iterable, List, NamedTuple, Optional, Union

ChatCommandArgs = NamedTuple('ChatCommandArgs',
                             [('database', DatabaseBase),
                              ('chat', Any),
                              ('tags', IrcMessageTagsReadOnly),
                              ('nick', str),
                              ('message', Message),
                              ('permissions', ChatPermissionSet),
                              ('timestamp', datetime)])

WhisperCommandArgs = NamedTuple('WhisperCommandArgs',
                                [('database', DatabaseBase),
                                 ('nick', str),
                                 ('message', Message),
                                 ('permissions', WhisperPermissionSet),
                                 ('timestamp', datetime)])

CustomFieldArgs = NamedTuple('CustomFieldArgs',
                             [('field', str),
                              ('param', str),
                              ('prefix', str),
                              ('suffix', str),
                              ('default', str),
                              ('message', Message),
                              ('channel', Any),
                              ('nick', str),
                              ('timestamp', datetime)])

CustomProcessArgs = NamedTuple('CustomProcessArgs',
                               [('database', DatabaseBase),
                                ('chat', Any),
                                ('tags', IrcMessageTagsReadOnly),
                                ('nick', str),
                                ('permissions', ChatPermissionSet),
                                ('broadcaster', str),
                                ('level', Optional[str]),
                                ('command', str),
                                ('messages', List[str])])

ManageBotArgs = NamedTuple('ManageBotArgs',
                           [('database', DatabaseBase),
                            ('send', Callable[[Union[str,Iterable[str]]], None]),
                            ('nick', str),
                            ('message', Message)])

ChatCommand = Callable[[ChatCommandArgs], bool]

WhisperCommand = Callable[[WhisperCommandArgs], bool]

CustomCommandField = Callable[[CustomFieldArgs], Optional[str]]

CustomCommandProcess = Callable[[CustomProcessArgs], None]

ManageBotCommand = Callable[[ManageBotArgs], bool]
