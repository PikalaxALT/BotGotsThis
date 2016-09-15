import unittest
from unittest.mock import Mock, patch

from source.data import Message
from source.database import DatabaseBase
from source.public.manage import banned
from tests.unittest.base_managebot import TestManageBot, send
from tests.unittest.mock_class import StrContains


class TestManageBotBanned(TestManageBot):
    def setUp(self):
        super().setUp()
        self.database.isChannelBannedReason.return_value = None

    def test_false(self):
        self.assertIs(banned.manageBanned(self.args), False)
        message = Message('!managebot')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)),
            False)
        message = Message('!managebot banned')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)),
            False)
        message = Message('!managebot banned no_action')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)),
            False)
        self.assertFalse(self.database.isChannelBannedReason.called)
        message = Message('!managebot banned no_action some_channel no_arg')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)),
            False)
        self.assertFalse(self.send.called)

    def test_need_reason(self):
        message = Message('!managebot banned add botgotsthis')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)), True)
        self.send.assert_called_once_with(
            StrContains(self.args.nick, 'Reason', 'specif'))

    @patch('source.public.manage.banned.list_banned_channels')
    def test_list(self, mock_list):
        mock_list.return_value = True
        message = Message('!managebot banned list')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)), True)
        mock_list.assert_called_once_with(self.database, self.send)

    @patch('source.public.manage.banned.insert_banned_channel')
    def test_add(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot banned add botgotsthis Kappa')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)), True)
        mock_add.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.database, self.send)

    @patch('source.public.manage.banned.insert_banned_channel')
    def test_insert(self, mock_add):
        mock_add.return_value = True
        message = Message('!managebot banned insert botgotsthis Kappa')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)), True)
        mock_add.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.database, self.send)

    @patch('source.public.manage.banned.delete_banned_channel')
    def test_delete(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot banned delete botgotsthis Kappa')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.database, self.send)

    @patch('source.public.manage.banned.delete_banned_channel')
    def test_del(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin del botgotsthis Kappa')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.database, self.send)

    @patch('source.public.manage.banned.delete_banned_channel')
    def test_remove(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin remove botgotsthis Kappa')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.database, self.send)

    @patch('source.public.manage.banned.delete_banned_channel')
    def test_rem(self, mock_delete):
        mock_delete.return_value = True
        message = Message('!managebot autojoin rem botgotsthis Kappa')
        self.assertIs(
            banned.manageBanned(self.args._replace(message=message)), True)
        mock_delete.assert_called_once_with(
            'botgotsthis', 'Kappa', 'botgotsthis', self.database, self.send)


class TestManageBotBannedListBannedChannels(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

    def test(self):
        self.database.listBannedChannels.return_value = []
        self.assertIs(
            banned.list_banned_channels(self.database, self.send), True)
        self.send.assert_called_once_with(StrContains('no'))

    @patch('source.public.library.message.messagesFromItems', autospec=True)
    def test_one(self, mock_messages):
        self.database.listBannedChannels.return_value = ['botgotsthis']
        mock_messages.return_value = ''
        self.assertIs(
            banned.list_banned_channels(self.database, self.send), True)
        mock_messages.assert_called_once_with(['botgotsthis'],
                                              StrContains('Banned'))
        self.send.assert_called_once_with('')

    @patch('source.public.library.message.messagesFromItems', autospec=True)
    def test_many(self, mock_messages):
        self.database.listBannedChannels.return_value = ['botgotsthis',
                                                         'megotsthis']
        mock_messages.return_value = ''
        self.assertIs(
            banned.list_banned_channels(self.database, self.send), True)
        mock_messages.assert_called_once_with(['botgotsthis', 'megotsthis'],
                                              StrContains('Banned'))
        self.send.assert_called_once_with('')


class TestManageBotBannedInsertBannedChannel(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

        patcher = patch('bot.utils.partChannel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_part = patcher.start()

        patcher = patch('bot.config', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()
        self.mock_config.botnick = 'botgotsthis'

    def test(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.addBannedChannel.return_value = True
        self.assertIs(
            banned.insert_banned_channel('megotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.addBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.database.discardAutoJoin.assert_called_once_with('megotsthis')
        self.mock_part.assert_called_once_with('megotsthis')
        self.send.assert_called_once_with(StrContains('megotsthis', 'ban'))

    def test_banned(self):
        self.database.isChannelBannedReason.return_value = 'DansGame'
        self.assertIs(
            banned.insert_banned_channel('megotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.assertFalse(self.database.addBannedChannel.called)
        self.assertFalse(self.database.discardAutoJoin.called)
        self.assertFalse(self.mock_part.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'ban', 'DansGame'))

    def test_banned_blank(self):
        self.database.isChannelBannedReason.return_value = ''
        self.assertIs(
            banned.insert_banned_channel('megotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.assertFalse(self.database.addBannedChannel.called)
        self.assertFalse(self.database.discardAutoJoin.called)
        self.assertFalse(self.mock_part.called)
        self.send.assert_called_once_with(StrContains('megotsthis', 'ban'))

    def test_database_error(self):
        self.database.isChannelBannedReason.return_value = None
        self.database.addBannedChannel.return_value = False
        self.assertIs(
            banned.insert_banned_channel('megotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.addBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.assertFalse(self.database.discardAutoJoin.called)
        self.assertFalse(self.mock_part.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'ban'))

    def test_bot(self):
        self.database.isChannelBannedReason.return_value = 'Kappa'
        self.assertIs(
            banned.insert_banned_channel('botgotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.assertFalse(self.database.isChannelBannedReason.called)
        self.assertFalse(self.database.addBannedChannel.called)
        self.assertFalse(self.database.discardAutoJoin.called)
        self.assertFalse(self.mock_part.called)
        self.send.assert_called_once_with(StrContains('not', 'ban', 'bot'))


class TestManageBotBannedDeleteBannedChannel(unittest.TestCase):
    def setUp(self):
        self.database = Mock(spec=DatabaseBase)
        self.send = Mock(spec=send)

    def test(self):
        self.database.isChannelBannedReason.return_value = 'Kappa'
        self.database.removeBannedChannel.return_value = True
        self.assertIs(
            banned.delete_banned_channel('megotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.removeBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.send.assert_called_once_with(StrContains('megotsthis', 'unban'))

    def test_blank(self):
        self.database.isChannelBannedReason.return_value = ''
        self.database.removeBannedChannel.return_value = True
        self.assertIs(
            banned.delete_banned_channel('megotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.removeBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.send.assert_called_once_with(StrContains('megotsthis', 'unban'))

    def test_not_banned(self):
        self.database.isChannelBannedReason.return_value = None
        self.assertIs(
            banned.delete_banned_channel('megotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.assertFalse(self.database.addBannedChannel.called)
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'ban'))

    def test_database_error(self):
        self.database.isChannelBannedReason.return_value = 'Kappa'
        self.database.removeBannedChannel.return_value = False
        self.assertIs(
            banned.delete_banned_channel('megotsthis', 'Kappa', 'botgotsthis',
                                         self.database, self.send),
            True)
        self.database.isChannelBannedReason.assert_called_once_with(
            'megotsthis')
        self.database.removeBannedChannel.assert_called_once_with(
            'megotsthis', 'Kappa', 'botgotsthis')
        self.send.assert_called_once_with(
            StrContains('megotsthis', 'not', 'unban'))