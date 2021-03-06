import asynctest

import bot  # noqa: F401

from datetime import datetime

from asynctest.mock import MagicMock, Mock, patch

import tests.unittest.asynctest_fix  # noqa: F401
from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from lib.cache import CacheStore
from lib.data import ChatCommandArgs
from lib.data.message import Message
from lib.data.permissions import ChatPermissionSet
from lib.database import DatabaseMain


class TestChannel(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.sessionData = {}
        self.data = Mock(spec=CacheStore)
        self.data.hasFeature.side_effect = lambda c, f: f in self.features
        self.database = MagicMock(spec=DatabaseMain)
        self.database.__aenter__.return_value = self.database
        self.database.__aexit__.return_value = False
        self.features = []
        self.database.hasFeature.side_effect = lambda c, f: f in self.features
        self.permissionSet = {
            'owner': False,
            'manager': False,
            'inOwnerChannel': False,
            'staff': False,
            'admin': False,
            'globalMod': False,
            'broadcaster': False,
            'moderator': False,
            'subscriber': False,
            'permitted': False,
            'chatModerator': False,
            'bannable': True,
            }
        self.permissions = MagicMock(spec=ChatPermissionSet)
        self.permissions.inOwnerChannel = False
        self.permissions.__getitem__.side_effect = \
            lambda k: self.permissionSet[k]
        self.args = ChatCommandArgs(
            self.data, self.channel, self.tags, 'botgotsthis', Message(''),
            self.permissions, self.now)

        patcher = patch.object(DatabaseMain, 'acquire')
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value = self.database
