﻿import copy
import random
import socket
from contextlib import suppress
from bot import data, globals, utils
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from ...api import twitch
from ...database.factory import getDatabase


def checkStreamsAndChannel(timestamp: datetime) -> None:
    if not globals.channels:
        return
    channels = copy.copy(globals.channels)  # type: Dict[str, data.Channel]
    onlineStreams = twitch.active_streams(
        channels.keys())  # type: Optional[twitch.OnlineStreams]
    if onlineStreams is None:
        return
    for channel in onlineStreams:  # --type: str
        chat = channels[channel]
        chat.twitchCache = timestamp
        (chat.streamingSince, chat.twitchStatus,
         chat.twitchGame) = onlineStreams[channel]

    for channel in channels:
        if channel in onlineStreams:
            continue
        channels[channel].streamingSince = None


def checkOfflineChannels(timestamp: datetime) -> None:
    if not globals.channels:
        return
    cacheDuration = timedelta(seconds=300)  # type: timedelta
    offlineChannels = [ch for ch in globals.channels.values()
                       if (not ch.isStreaming
                           and timestamp - ch.twitchCache >= cacheDuration)]  # type: List[data.Channel]
    if not offlineChannels:
        return
    chat = random.choice(offlineChannels)  # type: data.Channel
    current = twitch.channel_properties(chat.channel)  # type: Optional[twitch.TwitchStatus]
    if current is None:
        return
    (chat.streamingSince, chat.twitchStatus,
     chat.twitchGame) = current
    chat.twitchCache = timestamp


def checkChatServers(timestamp: datetime) -> None:
    cooldown = timedelta(seconds=3600)  # type: timedelta
    channels = copy.copy(globals.channels)  # type: Dict[str, data.Channel]
    toCheck = [c for c, ch in channels.items()
               if (timestamp - ch.serverCheck >= cooldown)]  # type: List[str]
    if not toCheck:
        return
    channel = random.choice(toCheck)  # type: str
    channels[channel].serverCheck = timestamp
    cluster = twitch.chat_server(channel)  # type: Optional[str]
    if (cluster is not None
            and (cluster not in globals.clusters
                 or globals.clusters[cluster] is not channels[channel].socket)):
        with getDatabase() as db:
            priority = db.getAutoJoinsPriority(channel)  # type: Union[int, float]
            utils.ensureServer(channel, priority, cluster)
            db.setAutoJoinServer(channel, cluster)
