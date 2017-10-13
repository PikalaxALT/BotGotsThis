﻿import asyncio
import bot
from bot import utils
from typing import Dict, List, Optional, Union  # noqa: F401
from lib.api import twitch
from lib.data import Send
from lib.data.message import Message
from lib.database import DatabaseMain


async def come(database: DatabaseMain,
               channel: str,
               send: Send) -> bool:
    bannedWithReason: Optional[str]
    bannedWithReason = await database.isChannelBannedReason(channel)
    if bannedWithReason is not None:
        send(f'Chat {channel} is banned from joining')
        return True
    priority: Union[float, int] = await database.getAutoJoinsPriority(channel)
    cluster: Optional[str] = await twitch.chat_server(channel)
    joinResult: Optional[bool] = utils.joinChannel(channel, priority, cluster)
    if joinResult is None:
        send(f'''\
Unable to join {channel} on a specified server according to twitch''')
    elif joinResult:
        send(f'Joining {channel}')
    else:
        ensureResult: int = utils.ensureServer(channel, priority, cluster)
        if ensureResult == utils.ENSURE_CORRECT:
            send(f'I am already in {channel}')
        elif ensureResult == utils.ENSURE_REJOIN:
            send(f'Moved {channel} to correct chat server')
        else:
            send('Unknown Error')
    return True


async def leave(channel: str,
                send: Send) -> bool:
    if channel == bot.config.botnick:
        return False
    send(f'Bye {channel}')
    await asyncio.sleep(1.0)
    utils.partChannel(channel)
    return True


async def auto_join(database: DatabaseMain,
                    channel: str,
                    send: Send,
                    message: Message) -> bool:
    bannedWithReason: Optional[str]
    bannedWithReason = await database.isChannelBannedReason(channel)
    if bannedWithReason is not None:
        send(f'Chat {channel} is banned from joining')
        return True

    if len(message) >= 2:
        removeMsgs: List[str] = ['0', 'false', 'no', 'remove', 'rem', 'delete',
                                 'del', 'leave', 'part']
        if message.lower[1] in removeMsgs:
            return await auto_join_delete(database, channel, send)
    return await auto_join_add(database, channel, send)


async def auto_join_add(database: DatabaseMain,
                        channel: str,
                        send: Send) -> bool:
    cluster: Optional[str] = await twitch.chat_server(channel)
    if cluster is None:
        send(f'Auto join for {channel} failed due to Twitch error')
        return True
    if cluster not in bot.globals.clusters:
        send(f'Auto join for {channel} failed due to unsupported chat server')
        return True
    result: bool = await database.saveAutoJoin(channel, 0, cluster)
    priority: Union[int, float] = await database.getAutoJoinsPriority(channel)
    if result is False:
        await database.setAutoJoinServer(channel, cluster)

    wasInChat: bool = not utils.joinChannel(channel, priority, cluster)
    rejoin: int = 0
    if wasInChat:
        rejoin = utils.ensureServer(channel, priority, cluster)

    if result and not wasInChat:
        send(f'''\
Auto join for {channel} is now enabled and joined {channel} chat''')
    elif result:
        if rejoin < 0:
            send(f'''\
Auto join for {channel} is now enabled and moved to the correct server''')
        else:
            send(f'Auto join for {channel} is now enabled')
    elif not wasInChat:
        send(f'''\
Auto join for {channel} is already enabled but now joined {channel} chat''')
    else:
        if rejoin < 0:
            send(f'''\
Auto join for {channel} is already enabled and moved to the correct server''')
        else:
            send(f'''\
Auto join for {channel} is already enabled and already in chat''')
    return True


async def auto_join_delete(database: DatabaseMain,
                           channel: str,
                           send: Send) -> bool:
    result: bool = await database.discardAutoJoin(channel)
    if result:
        send(f'Auto join for {channel} is now disabled')
    else:
        send(f'Auto join for {channel} was never enabled')
    return True