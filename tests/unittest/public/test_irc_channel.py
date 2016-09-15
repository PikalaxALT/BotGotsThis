import unittest
from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from datetime import datetime
from source import channel
from source.data import Message
from source.database import DatabaseBase
from unittest.mock import MagicMock, Mock, PropertyMock, patch


class TestChannel(unittest.TestCase):
    def setUp(self):
        self.tags = IrcMessageTags(IrcMessageTags.parseTags(
            'display-name=BotGotsThis;id=0;subscriber=0;turbo=0;mod=1;'
            'user-type=mod;badges=broadcaster/1;color=#FFFFFF;emotes=;'
            'room-id=1;user-id=1'))
        self.channel = Mock(spec=Channel)
        self.now = datetime(2000, 1, 1)

    @patch('source.channel.chatCommand', autospec=True)
    def test_parse(self, mock_chatCommand):
        channel.parse(self.channel, self.tags, 'botgotsthis', 'Kappa',
                      self.now)
        self.assertTrue(mock_chatCommand.called)

    @patch('source.channel.chatCommand', autospec=True)
    def test_parse_empty(self, mock_chatCommand):
        channel.parse(self.channel, self.tags, 'botgotsthis', '', self.now)
        self.assertFalse(mock_chatCommand.called)

    @patch('source.channel.chatCommand', autospec=True)
    def test_parse_spaces(self, mock_chatCommand):
        channel.parse(self.channel, self.tags, 'botgotsthis', '  ', self.now)
        self.assertFalse(mock_chatCommand.called)

    @patch('source.database.factory.getDatabase', autospec=True)
    @patch('source.channel.commandsToProcess', autospec=True)
    def test_chatCommand(self, mock_commands, mock_database):
        command1 = Mock(spec=lambda args: False, return_value=False)
        command2 = Mock(spec=lambda args: False, return_value = True)
        command3 = Mock(spec=lambda args: False, return_value = False)
        mock_commands.return_value = [command1, command2, command3]
        database = MagicMock(spec=DatabaseBase)
        database.__exit__.return_value = True
        mock_database.return_value = database
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        channel.chatCommand(self.channel, self.tags, 'botgotsthis', message,
                            self.now)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command1.call_count, 1)
        self.assertEqual(command2.call_count, 1)
        self.assertEqual(command3.call_count, 0)

    @patch('bot.utils.logException', autospec=True)
    @patch('source.database.factory.getDatabase', autospec=True)
    @patch('source.channel.commandsToProcess', autospec=True)
    def test_chatCommand_except(self, mock_commands, mock_database, mock_log):
        command = Mock(spec=lambda args: False, side_effect=Exception)
        mock_commands.return_value = [command, command]
        database = MagicMock(spec=DatabaseBase)
        database.__exit__.return_value = False
        mock_database.return_value = database
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        channel.chatCommand(self.channel, self.tags, 'botgotsthis', message,
                            self.now)
        self.assertEqual(mock_commands.call_count, 1)
        self.assertEqual(command.call_count, 1)
        self.assertTrue(mock_log.called)

    @patch('bot.utils.logException', autospec=True)
    @patch('source.database.factory.getDatabase', autospec=True)
    @patch('source.channel.commandsToProcess', autospec=True)
    def test_chatCommand_database_except(self, mock_commands, mock_database, mock_log):
        mock_database.side_effect = Exception
        message = Mock(spec=Message)
        type(message).command = PropertyMock(return_value='Kappa')
        channel.chatCommand(self.channel, self.tags, 'botgotsthis', message,
                            self.now)
        self.assertFalse(mock_commands.called)
        self.assertTrue(mock_log.called)


class TestChannelCommandToProcess(unittest.TestCase):
    def setUp(self):
        patcher = patch('lists.channel', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_list = patcher.start()
        self.mock_list.filterMessage = []
        self.mock_list.commands = {}
        self.mock_list.commandsStartWith = {}
        self.mock_list.processNoCommand = []

        self.command1 = lambda args: False
        self.command2 = lambda args: False
        self.command3 = lambda args: False
        self.command4 = lambda args: False

    def test_commandsToProcess_empty(self):
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_specific(self):
        self.mock_list.commands['!kappa'] = self.command1
        self.assertEqual(
            list(channel.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_specific_no_match(self):
        self.mock_list.commands['!kappahd'] = self.command1
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_specific_none(self):
        self.mock_list.commands['!kappa'] = None
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith(self):
        self.mock_list.commandsStartWith['!k'] = self.command1
        self.assertEqual(
            list(channel.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_startswith_exact(self):
        self.mock_list.commandsStartWith['!kappa'] = self.command1
        self.assertEqual(
            list(channel.commandsToProcess('!kappa')), [self.command1])

    def test_commandsToProcess_startswith_none(self):
        self.mock_list.commandsStartWith['!k'] = None
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith_no_match(self):
        self.mock_list.commandsStartWith['!kevinturtle'] = self.command1
        self.assertEqual(list(channel.commandsToProcess('!kappa')), [])

    def test_commandsToProcess_startswith_multiple(self):
        self.mock_list.commandsStartWith['!k'] = self.command1
        self.mock_list.commandsStartWith['!ka'] = self.command2
        self.assertCountEqual(
            list(channel.commandsToProcess('!kappa')),
            [self.command1, self.command2])

    def test_commandsToProcess_specific_startswith(self):
        self.mock_list.commands['!kappa'] = self.command1
        self.mock_list.commandsStartWith['!k'] = self.command2
        self.mock_list.commandsStartWith['!ka'] = self.command3
        self.assertCountEqual(
            list(channel.commandsToProcess('!kappa')),
            [self.command1, self.command2, self.command3])

    def test_commandsToProcess_filter(self):
        self.mock_list.filterMessage.append(self.command1)
        self.assertCountEqual(
            list(channel.commandsToProcess('')), [self.command1])

    def test_commandsToProcess_nocommand(self):
        self.mock_list.processNoCommand.append(self.command1)
        self.assertCountEqual(
            list(channel.commandsToProcess('')), [self.command1])

    def test_commandsToProcess_ordering(self):
        self.mock_list.filterMessage.append(self.command1)
        self.mock_list.commands['!kappa'] = self.command2
        self.mock_list.commandsStartWith['!k'] = self.command3
        self.mock_list.processNoCommand.append(self.command4)
        self.assertCountEqual(
            list(channel.commandsToProcess('!kappa')),
            [self.command1, self.command2, self.command3, self.command4])