import unittest
from bot.coroutine.connection import ConnectionHandler
from bot.data import Channel, ConnectionReset
from bot.twitchmessage import IrcMessage, IrcMessageParams
from datetime import datetime
from lib import ircmessage
from unittest.mock import Mock, patch


class PublicTestIrcMessage(unittest.TestCase):
    def setUp(self):
        self.connection = Mock(spec=ConnectionHandler)
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircOps = set()
        self.channel.ircUsers = set()
        self.connection.channels = {'botgotsthis': self.channel}
        self.now = datetime(2000, 1, 1)

        patcher = patch('lib.ircmessage.utils.logIrcMessage', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_log = patcher.start()

    @patch.dict('lib.ircmessage.ircHandlers')
    @patch('bot.globals')
    @patch('importlib.import_module')
    @patch('lib.ircmessage.log_channel_message')
    def test_parseMessage(self, mock_log, mock_import_module, mock_globals):
        mock_globals.pkgs = ['botgotsthis']
        mock_parse = Mock()
        mock_import_module.return_value = Mock()
        mock_import_module.return_value.parseMessage = mock_parse
        ircmessage.ircHandlers['KAPPA'] = Mock()
        ircmessage.ircHandlers['TWITCH'] = Mock()
        ircmessage.parseMessage(self.connection, 'KAPPA', self.now)
        self.assertTrue(ircmessage.ircHandlers['KAPPA'].called)
        self.assertFalse(ircmessage.ircHandlers['TWITCH'].called)
        self.assertTrue(mock_log.called)
        self.assertTrue(mock_parse.called)

    @patch.dict('lib.ircmessage.ircHandlers')
    def test_registerIrc(self):
        @ircmessage.registerIrc('KAPPA')
        def irc_kappa(socket, message, timestamp):
            pass
        self.assertIn('KAPPA', ircmessage.ircHandlers)
        self.assertIs(ircmessage.ircHandlers['KAPPA'], irc_kappa)

    def test_log_channel_message(self):
        message = IrcMessage(command='PRIVMSG',
                             params=IrcMessageParams(middle='#botgotsthis',
                                                     trailing=''))
        ircmessage.log_channel_message(message, self.now)
        self.assertTrue(self.mock_log.called)

    def test_log_channel_message_not(self):
        ircmessage.log_channel_message(IrcMessage(command=0), self.now)
        self.assertFalse(self.mock_log.called)

    @patch('bot.config', autospec=True)
    @patch('lib.channel.parse', autospec=True)
    def test_log_irc_privmsg(self, mock_parse, mock_config):
        mock_config.botnick = 'botgotsthis'
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PRIVMSG '
            '#botgotsthis :Hello Kappa')
        ircmessage.irc_privmsg(self.connection, message, self.now)
        self.assertTrue(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    @patch('bot.config', autospec=True)
    @patch('lib.channel.parse', autospec=True)
    def test_log_irc_privmsg_no_channel(self, mock_parse, mock_config):
        mock_config.botnick = 'botgotsthis'
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PRIVMSG '
            '#megotsthis :Hello Kappa')
        ircmessage.irc_privmsg(self.connection, message, self.now)
        self.assertFalse(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    @patch('bot.config', autospec=True)
    @patch('lib.channel.parse', autospec=True)
    def test_log_irc_privmsg_mention(self, mock_parse, mock_config):
        mock_config.botnick = 'botgotsthis'
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PRIVMSG '
            '#botgotsthis :botgotsthis')
        ircmessage.irc_privmsg(self.connection, message, self.now)
        self.assertTrue(mock_parse.called)
        self.assertGreaterEqual(self.mock_log.call_count, 2)

    @patch('bot.config', autospec=True)
    @patch('lib.whisper.parse', autospec=True)
    def test_log_irc_whisper(self, mock_parse, mock_config):
        mock_config.botnick = 'botgotsthis'
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@megotsthis.tmi.twitch.tv WHISPER '
            'botgotsthis :Kappa')
        ircmessage.irc_whisper(self.connection, message, self.now)
        self.assertTrue(mock_parse.called)
        self.assertGreaterEqual(self.mock_log.call_count, 3)

    @patch('lib.irccommand.notice.parse', autospec=True)
    def test_log_irc_notice(self, mock_parse):
        message = IrcMessage.fromMessage(
            '@msg-id=bad_timeout_broadcaster :tmi.twitch.tv NOTICE '
            '#botgotsthis :You cannot timeout the broadcaster.')
        ircmessage.irc_notice(self.connection, message, self.now)
        self.assertTrue(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    @patch('lib.irccommand.clearchat.parse', autospec=True)
    def test_log_irc_clearchat(self, mock_parse):
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv CLEARCHAT #botgotsthis')
        ircmessage.irc_clearchat(self.connection, message, self.now)
        self.assertTrue(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_roomstate(self):
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv ROOMSTATE #megotsthis')
        ircmessage.irc_clearchat(self.connection, message, self.now)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_hosttarget(self):
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv ROOMSTATE #megotsthis')
        ircmessage.irc_clearchat(self.connection, message, self.now)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_mode_plus_o(self):
        message = IrcMessage.fromMessage(
            ':jtv MODE #botgotsthis +o botgotsthis')
        ircmessage.irc_mode(self.connection, message, self.now)
        self.assertEqual(self.channel.ircOps, {'botgotsthis'})

    def test_log_irc_mode_plus_o_duplicating(self):
        self.channel.ircOps = {'botgotsthis'}
        message = IrcMessage.fromMessage(
            ':jtv MODE #botgotsthis +o botgotsthis')
        ircmessage.irc_mode(self.connection, message, self.now)
        self.assertEqual(self.channel.ircOps, {'botgotsthis'})

    def test_log_irc_mode_minus_o_empty(self):
        message = IrcMessage.fromMessage(
            ':jtv MODE #botgotsthis -o botgotsthis')
        ircmessage.irc_mode(self.connection, message, self.now)
        self.assertEqual(self.channel.ircOps, set())

    def test_log_irc_join(self):
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv JOIN '
            '#botgotsthis')
        ircmessage.irc_join(self.connection, message, self.now)
        self.assertEqual(self.channel.ircUsers, {'botgotsthis'})

    def test_log_irc_353(self):
        message = IrcMessage.fromMessage(
            ':botgotsthis.tmi.twitch.tv 353 botgotsthis = #botgotsthis '
            ':botgotsthis')
        ircmessage.irc_353(self.connection, message, self.now)
        self.assertEqual(self.channel.ircUsers, {'botgotsthis'})
        self.assertTrue(self.mock_log.called)

    def test_log_irc_366(self):
        message = IrcMessage.fromMessage(
            ':botgotsthis.tmi.twitch.tv 366 botgotsthis #botgotsthis '
            ':End of /NAMES list')
        ircmessage.irc_353(self.connection, message, self.now)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_part(self):
        self.channel.ircUsers.add('botgotsthis')
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PART '
            '#botgotsthis')
        ircmessage.irc_part(self.connection, message, self.now)
        self.assertEqual(self.channel.ircUsers, set())

    def test_log_irc_part_empty(self):
        message = IrcMessage.fromMessage(
            ':botgotsthis!botgotsthis@botgotsthis.tmi.twitch.tv PART '
            '#botgotsthis')
        ircmessage.irc_part(self.connection, message, self.now)
        self.assertEqual(self.channel.ircUsers, set())

    def test_log_irc_ping(self):
        message = IrcMessage.fromMessage(
            'PING :tmi.twitch.tv')
        ircmessage.irc_ping(self.connection, message, self.now)
        self.assertTrue(self.connection.ping.called)

    @patch('bot.config', autospec=True)
    def test_log_irc_pong(self, mock_config):
        mock_config.botnick = 'botgotsthis'
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv PONG tmi.twitch.tv :botgotsthis')
        ircmessage.irc_pong(self.connection, message, self.now)
        self.assertEqual(self.connection.lastPing, self.now)

    @patch('lib.irccommand.userstate.parse', autospec=True)
    def test_log_irc_userstate(self, mock_parse):
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv CLEARCHAT #botgotsthis')
        ircmessage.irc_userstate(self.connection, message, self.now)
        self.assertTrue(mock_parse.called)
        self.assertTrue(self.mock_log.called)

    def test_log_irc_reconnect(self):
        message = IrcMessage.fromMessage(
            ':tmi.twitch.tv RECONNECT')
        with self.assertRaises(ConnectionReset):
            ircmessage.irc_reconnect(self.connection, message, self.now)
