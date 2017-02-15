﻿import bot.globals
import copy
import random
from bot import data, utils
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from ...api import twitch
from ...database import factory


def checkTwitchIds(timestamp: datetime) -> None:
    if not bot.globals.channels:
        return
    channels = [c for c in bot.globals.channels
                if c not in bot.globals.twitchId]  # type: List[str]
    cacheDuration = timedelta(hours=1)
    channels += [c for c in bot.globals.twitchId
                 if c not in channels
                 if bot.globals.twitchIdCache[c] + cacheDuration <= timestamp]
    if not channels:
        return

    ids = twitch.getTwitchIds(channels)  # type: Optional[Dict[str, str]]
    if ids is None:
        return
    for channel, id in ids.items():  # type: str, str
        utils.saveTwitchId(channel, id, timestamp)
    for channel in bot.globals.channels:
        if channel in ids:
            continue
        utils.saveTwitchId(channel, None, timestamp)


def checkStreamsAndChannel(timestamp: datetime) -> None:
    if not bot.globals.channels:
        return
    channels = copy.copy(bot.globals.channels)  # type: Dict[str, data.Channel]
    onlineStreams = twitch.active_streams(
        channels.keys())  # type: Optional[twitch.OnlineStreams]
    if onlineStreams is None:
        return
    for channel in onlineStreams:  # type: str
        chat = channels[channel]
        chat.twitchCache = timestamp
        (chat.streamingSince, chat.twitchStatus,
         chat.twitchGame, chat.community) = onlineStreams[channel]
        if chat.community is not None:
            bot.utils.loadTwitchCommunity(chat.community)

    for channel in channels:
        if channel in onlineStreams:
            continue
        channels[channel].streamingSince = None


def checkOfflineChannels(timestamp: datetime) -> None:
    if not bot.globals.channels:
        return
    cacheDuration = timedelta(seconds=300)  # type: timedelta
    offlineChannels = [ch for ch in bot.globals.channels.values()
                       if (not ch.isStreaming
                           and timestamp - ch.twitchCache >= cacheDuration)]  # type: List[data.Channel]
    if not offlineChannels:
        return
    if 'offlineCheck' not in bot.globals.globalSessionData:
        bot.globals.globalSessionData['offlineCheck'] = []
    bot.globals.globalSessionData['offlineCheck'] = [
        t for t in bot.globals.globalSessionData['offlineCheck']
        if t >= timestamp - timedelta(minutes=1)]
    if len(bot.globals.globalSessionData['offlineCheck']) >= 40:
        return
    chat = random.choice(offlineChannels)  # type: data.Channel
    chat.twitchCache = timestamp
    current = twitch.channel_properties(chat.channel)  # type: Optional[twitch.TwitchStatus]
    if current is None:
        chat.twitchCache = timestamp - cacheDuration + timedelta(seconds=60)
        return
    (chat.streamingSince, chat.twitchStatus,
     chat.twitchGame, shouldBeNone) = current
    community = twitch.channel_community(chat.channel)  # type: twitch.TwitchCommunity
    if community is not None:
        chat.community = community.id
        bot.utils.saveTwitchCommunity(community.name, community.id, timestamp)
    bot.globals.globalSessionData['offlineCheck'].append(timestamp)


def checkChatServers(timestamp: datetime) -> None:
    cooldown = timedelta(seconds=3600)  # type: timedelta
    channels = copy.copy(bot.globals.channels)  # type: Dict[str, data.Channel]
    toCheck = [c for c, ch in channels.items()
               if (timestamp - ch.serverCheck >= cooldown)]  # type: List[str]
    if not toCheck:
        return
    channel = random.choice(toCheck)  # type: str
    channels[channel].serverCheck = timestamp
    cluster = twitch.chat_server(channel)  # type: Optional[str]
    if cluster is None:
        return
    if (cluster in bot.globals.clusters
            and bot.globals.clusters[cluster] is channels[channel].socket):
        return
    with factory.getDatabase() as db:
        priority = db.getAutoJoinsPriority(channel)  # type: Union[int, float]
        utils.ensureServer(channel, priority, cluster)
        db.setAutoJoinServer(channel, cluster)
