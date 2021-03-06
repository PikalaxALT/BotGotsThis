import asyncio
from datetime import datetime, timedelta

import asynctest
from asynctest.mock import MagicMock, Mock, PropertyMock, call, patch

from bot.data import Channel
from lib.cache import CacheStore
from lib.api.twitch import TwitchCommunity, TwitchStatus
from ..tasks import twitch


class TestTasksTwitchBase(asynctest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)

        self.data = MagicMock(spec=CacheStore)
        self.data.__aenter__.return_value = self.data
        self.data.__aexit__.return_value = True

        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'

        patcher = patch('bot.globals', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_globals = patcher.start()
        self.mock_globals.channels = {'botgotsthis': self.channel}
        self.mock_globals.globalSessionData = {}

        patcher = patch('lib.cache.get_cache')
        self.addCleanup(patcher.stop)
        self.mock_cache = patcher.start()
        self.mock_cache.return_value = self.data


class TestTasksTwitchIds(TestTasksTwitchBase):
    async def test(self):
        await twitch.checkTwitchIds(self.now)
        self.data.twitch_load_ids.assert_called_once_with(['botgotsthis'])


class TestTasksTwitchStreams(TestTasksTwitchBase):
    def setUp(self):
        super().setUp()

        self.cache_property = PropertyMock(return_value=self.now)
        type(self.channel).twitchCache = self.cache_property

        self.streaming_property = PropertyMock(return_value=None)
        type(self.channel).streamingSince = self.streaming_property

        self.status_property = PropertyMock(return_value=None)
        type(self.channel).twitchStatus = self.status_property

        self.game_property = PropertyMock(return_value=None)
        type(self.channel).twitchGame = self.game_property

        self.channel.sessionData = {}

    @patch('lib.api.twitch.active_streams')
    async def test_streams_empty(self, mock_active):
        self.mock_globals.channels = {}
        await twitch.checkStreamsAndChannel(self.now)
        self.assertFalse(mock_active.called)

    @patch('lib.api.twitch.active_streams')
    async def test_streams_none(self, mock_active):
        mock_active.return_value = None
        await twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('lib.api.twitch.active_streams')
    async def test_streams(self, mock_active):
        streamed = datetime(1999, 1, 1)
        mock_active.return_value = {
            'botgotsthis': TwitchStatus(streamed, 'Kappa', 'Creative', [])
            }
        await twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.cache_property.assert_called_once_with(self.now)
        self.streaming_property.assert_called_once_with(streamed)
        self.status_property.assert_called_once_with('Kappa')
        self.game_property.assert_called_once_with('Creative')

    @patch('lib.api.twitch.active_streams')
    async def test_streams_offline(self, mock_active):
        mock_active.return_value = {}
        await twitch.checkStreamsAndChannel(self.now)
        self.assertTrue(mock_active.called)
        self.assertFalse(self.cache_property.called)
        self.streaming_property.assert_called_once_with(None)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)

    @patch('lib.api.twitch.channel_community')
    @patch('lib.api.twitch.channel_properties')
    async def test_offline_empty(self, mock_channel, mock_community):
        self.mock_globals.channels = {}
        await twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)
        self.assertFalse(mock_community.called)
        self.assertFalse(self.data.twitch_save_community.called)

    @patch('lib.api.twitch.channel_community')
    @patch('lib.api.twitch.channel_properties')
    async def test_offline_streaming(self, mock_channel, mock_community):
        self.channel.isStreaming = True
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.assertFalse(self.cache_property.called)
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)
        self.assertFalse(mock_community.called)
        self.assertFalse(self.data.twitch_save_community.called)

    @patch('lib.api.twitch.channel_community')
    @patch('lib.api.twitch.channel_properties')
    async def test_offline_recent(self, mock_channel, mock_community):
        mock_community.return_value = None
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now
        await twitch.checkOfflineChannels(self.now)
        self.assertFalse(mock_channel.called)
        self.cache_property.assert_called_once_with()
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)
        self.assertFalse(mock_community.called)
        self.assertFalse(self.data.twitch_save_community.called)

    @patch('lib.api.twitch.channel_community')
    @patch('lib.api.twitch.channel_properties')
    async def test_offline_none(self, mock_channel, mock_community):
        mock_community.return_value = None
        mock_channel.return_value = None
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls(
            [call(), call(self.now),
             call(self.now - timedelta(seconds=240))])
        self.assertFalse(self.streaming_property.called)
        self.assertFalse(self.status_property.called)
        self.assertFalse(self.game_property.called)
        self.assertFalse(mock_community.called)
        self.assertFalse(self.data.twitch_save_community.called)

    @patch('lib.api.twitch.channel_community')
    @patch('lib.api.twitch.channel_properties')
    async def test_offline(self, mock_channel, mock_community):
        mock_community.return_value = None
        mock_channel.return_value = TwitchStatus(None, 'Keepo', 'Music', None)
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls([call(), call(self.now)])
        self.streaming_property.assert_called_once_with(None)
        self.status_property.assert_called_once_with('Keepo')
        self.game_property.assert_called_once_with('Music')
        mock_community.assert_called_once_with('botgotsthis')
        self.assertFalse(self.data.twitch_save_community.called)

    @patch('lib.api.twitch.channel_community')
    @patch('lib.api.twitch.channel_properties')
    async def test_offline_multiple(self, mock_channel, mock_community):
        async def wait(*args):
            await asyncio.sleep(0.2)
            return TwitchStatus(None, 'Keepo', 'Music', None)

        async def call_0():
            await twitch.checkOfflineChannels(self.now)

        async def call_1():
            await asyncio.sleep(0.1)
            await twitch.checkOfflineChannels(self.now)

        mock_community.return_value = None
        mock_channel.side_effect = wait
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await asyncio.gather(call_0(), call_1())
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls([call(), call(self.now)])
        self.streaming_property.assert_called_once_with(None)
        self.status_property.assert_called_once_with('Keepo')
        self.game_property.assert_called_once_with('Music')
        mock_community.assert_called_once_with('botgotsthis')
        self.assertFalse(self.data.twitch_save_community.called)

    @patch('lib.api.twitch.channel_community')
    @patch('lib.api.twitch.channel_properties')
    async def test_offline_community_empty(self, mock_channel, mock_community):
        mock_community.return_value = []
        mock_channel.return_value = TwitchStatus(None, 'Keepo', 'Music', None)
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls([call(), call(self.now)])
        self.streaming_property.assert_called_once_with(None)
        self.status_property.assert_called_once_with('Keepo')
        self.game_property.assert_called_once_with('Music')
        mock_community.assert_called_once_with('botgotsthis')
        self.assertFalse(self.data.twitch_save_community.called)

    @patch('lib.api.twitch.channel_community')
    @patch('lib.api.twitch.channel_properties')
    async def test_offline_community(self, mock_channel, mock_community):
        mock_community.return_value = [TwitchCommunity('1', 'BotGotsThis')]
        mock_channel.return_value = TwitchStatus(None, 'Keepo', 'Music', None)
        self.channel.isStreaming = False
        self.cache_property.return_value = self.now - timedelta(hours=1)
        await twitch.checkOfflineChannels(self.now)
        mock_channel.assert_called_once_with('botgotsthis')
        self.cache_property.assert_has_calls([call(), call(self.now)])
        self.streaming_property.assert_called_once_with(None)
        self.status_property.assert_called_once_with('Keepo')
        self.game_property.assert_called_once_with('Music')
        mock_community.assert_called_once_with('botgotsthis')
        self.data.twitch_save_community.assert_called_once_with(
            '1', 'BotGotsThis')
