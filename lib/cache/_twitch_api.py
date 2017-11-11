import asyncio
import json
from typing import Any, Awaitable, Dict, List, Optional, cast  # noqa: F401

from ._abc import AbcCacheStore
from . import store
from ..api import twitch


class TwitchApisMixin(AbcCacheStore):
    async def twitch_num_followers(self, user: str) -> Optional[int]:
        key: str = f'twitch:{user}:following'
        numFollowers: Optional[int]
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            data: store.CacheStore = cast(store.CacheStore, self)
            numFollowers = await twitch.num_followers(user, data=data)
            expire: int = 3600 if numFollowers else 300
            await self.redis.setex(key, expire, json.dumps(numFollowers))
        else:
            numFollowers = json.loads(value)
        return numFollowers

    def _twitchIdIdKey(self, id: str) -> str:
        return f'id:id:{id}'

    def _twitchIdUserKey(self, user: str) -> str:
        return f'id:user:{user}'

    async def twitch_load_id(self, user: str) -> bool:
        key: str = self._twitchIdUserKey(user)
        if await self.redis.exists(key):
            return True
        ids: Optional[Dict[str, str]] = await twitch.getTwitchIds([user])
        if ids is None:
            return False
        if user in ids:
            await self.twitch_save_id(ids[user], user)
        else:
            await self.twitch_save_id(None, user)
        return True

    async def twitch_save_id(self, id: Optional[str], user: str) -> bool:
        # 6 hours normally or 1 hour for non existent id
        expire: int = 21600 if id is not None else 3600
        tasks: List[Awaitable[Any]] = [
            self.redis.setex(self._twitchIdUserKey(user), expire,
                             json.dumps(id)),
        ]
        if id is not None:
            tasks.append(self.redis.setex(self._twitchIdIdKey(id), expire,
                                          json.dumps(user)))
        await asyncio.gather(*tasks)
        return True

    async def twitch_has_id(self, user: str) -> bool:
        key: str = self._twitchIdUserKey(user)
        return await self.redis.exists(key)

    async def twitch_is_valid_user(self, user: str) -> Optional[bool]:
        if not await self.twitch_load_id(user):
            return None
        return await self.twitch_get_id(user) is not None

    async def twitch_get_id(self, user: str) -> Optional[str]:
        key: str = self._twitchIdUserKey(user)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def twitch_get_user(self, id: str) -> Optional[str]:
        key: str = self._twitchIdIdKey(id)
        value: Optional[str] = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)
