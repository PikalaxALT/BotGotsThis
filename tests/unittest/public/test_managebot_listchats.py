from unittest.mock import patch

from source.public.manage import listchats
from tests.unittest.base_managebot import TestManageBot
from tests.unittest.mock_class import StrContains


class TestManageBotListChats(TestManageBot):
    @patch('source.public.library.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    def test_no_channels(self, mock_globals, mock_messages):
        mock_globals.channels = ''
        self.assertIs(listchats.manageListChats(self.args), True)
        self.assertFalse(mock_messages.called)
        self.send.assert_called_once_with(StrContains('not', 'in'))

    @patch('source.public.library.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    def test_one_channel(self, mock_globals, mock_messages):
        mock_globals.channels = {'botgotsthis': None}
        mock_messages.return_value = ''
        self.assertIs(listchats.manageListChats(self.args), True)
        mock_messages.assert_called_once_with(['botgotsthis'],
                                              StrContains('Chats'))
        self.send.assert_called_once_with('')

    @patch('source.public.library.message.messagesFromItems', autospec=True)
    @patch('bot.globals', autospec=True)
    def test_many_channel(self, mock_globals, mock_messages):
        mock_globals.channels = {'botgotsthis': None,
                                 'mebotsthis': None,
                                 'megotsthis': None}
        mock_messages.return_value = ''
        self.assertIs(listchats.manageListChats(self.args), True)
        mock_messages.assert_called_once_with(
            ['botgotsthis', 'mebotsthis', 'megotsthis'], StrContains('Chats'))
        self.send.assert_called_once_with('')