import socket
import unittest
import urllib.error
from bot.data import Channel
from datetime import datetime, timedelta
from http.client import HTTPResponse
from source.database import DatabaseBase
from source.data.message import Message
from source.public.channel import block_url
from unittest.mock import ANY, Mock, call, patch
from unittests.public.test_channel import TestChannel


@patch('source.public.channel.block_url.check_domain_redirect', autospec=True)
class TestChannelBlockUrlFilterNoUrl(TestChannel):
    def test_nomod(self, mock_check):
        self.assertIs(block_url.filterNoUrlForBots(self.args), False)
        self.assertFalse(mock_check.called)

    def test_no_match(self, mock_check):
        self.permissionSet['chatModerator'] = True
        self.features.append('nourlredirect')
        self.assertIs(block_url.filterNoUrlForBots(self.args), False)
        self.assertFalse(mock_check.called)

    def test_check(self, mock_check):
        message = Message('megotsthis.com')
        self.args = self.args._replace(message=message)
        self.permissionSet['chatModerator'] = True
        self.features.append('nourlredirect')
        self.assertIs(block_url.filterNoUrlForBots(self.args), False)
        mock_check.assert_called_once_with(self.channel, 'botgotsthis',
                                           message, self.now)


class TestChannelBlockUrlCheckDomainRedirect(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.now = datetime(2000, 1, 1)

        patcher = patch('source.public.channel.block_url.twitch.num_followers',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_followers = patcher.start()

        patcher = patch('source.public.channel.block_url.utils.logIrcMessage',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_log = patcher.start()

        patcher = patch('source.public.channel.block_url.utils.logException',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_except = patcher.start()

        patcher = patch(
            'source.public.channel.block_url.urllib.request.urlopen',
            autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_request = patcher.start()
        self.response = Mock(spec=HTTPResponse)
        self.mock_request.return_value.__enter__.return_value = self.response

        patcher = patch('source.public.channel.block_url.compare_domains',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_compare = patcher.start()
        self.mock_compare.return_value = False

        patcher = patch(
            'source.public.channel.block_url.handle_different_domains',
            autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_handle = patcher.start()

    def test_no_followers(self):
        self.mock_followers.return_value = 0
        message = Message('twitch.tv')
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.assertFalse(self.mock_log.called)
        self.assertFalse(self.mock_except.called)
        self.assertFalse(self.mock_request.called)
        self.assertFalse(self.mock_compare.called)
        self.assertFalse(self.mock_handle.called)

    def test(self):
        self.mock_followers.return_value = 1
        self.mock_compare.return_value = True
        message = Message('twitch.tv')
        self.response.geturl.return_value = 'http://megotsthis.com'
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.mock_request.assert_called_once_with(ANY)
        self.response.geturl.assert_called_once_with()
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://megotsthis.com',
            chat=self.channel, nick='botgotsthis', timestamp=self.now)
        self.mock_handle.assert_called_once_with(
            self.channel, 'botgotsthis', message)
        self.assertFalse(self.mock_except.called)

    def test_same_domain(self):
        self.mock_followers.return_value = 1
        message = Message('twitch.tv')
        self.response.geturl.return_value = 'http://twitch.tv'
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.mock_request.assert_called_once_with(ANY)
        self.response.geturl.assert_called_once_with()
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='botgotsthis', timestamp=self.now)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    def test_404_error(self):
        self.mock_followers.return_value = 1
        message = Message('twitch.tv')
        self.mock_request.side_effect = urllib.error.HTTPError(
            'http://twitch.tv', 404, None, {}, 0)
        self.response.geturl.return_value = 'http://twitch.tv'
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.mock_request.assert_called_once_with(ANY)
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='botgotsthis', timestamp=self.now)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    def test_502_error(self):
        self.mock_followers.return_value = 1
        message = Message('twitch.tv')
        self.mock_request.side_effect = urllib.error.HTTPError(
            'http://twitch.tv', 502, None, {}, 0)
        self.response.geturl.return_value = 'http://twitch.tv'
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.mock_request.assert_called_once_with(ANY)
        self.mock_compare.assert_called_once_with(
            'http://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='botgotsthis', timestamp=self.now)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    def test_urlerror_no_dns(self):
        self.mock_followers.return_value = 1
        message = Message('twitch.tv')
        self.mock_request.side_effect = urllib.error.URLError(
            OSError(socket.EAI_NONAME, 'no name'))
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.mock_request.assert_called_once_with(ANY)
        self.assertFalse(self.mock_compare.called)
        self.assertFalse(self.mock_except.called)

    def test_urlerror_other(self):
        self.mock_followers.return_value = 1
        message = Message('twitch.tv')
        self.mock_request.side_effect = urllib.error.URLError('error')
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.mock_request.assert_called_once_with(ANY)
        self.mock_except.assert_called_once_with(ANY, ANY)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_compare.called)

    def test_exception(self):
        self.mock_followers.return_value = 1
        message = Message('twitch.tv')
        self.mock_request.side_effect = Exception
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.mock_request.assert_called_once_with(ANY)
        self.mock_except.assert_called_once_with(ANY, ANY)
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_compare.called)

    def test_multiple(self):
        self.mock_followers.return_value = 1
        message = Message('https://twitch.tv megotsthis.com')
        self.response.geturl.side_effect = ['http://twitch.tv',
                                            'https://twitch.tv']
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.assertEqual(self.mock_request.call_count, 2)
        self.assertEqual(self.response.geturl.call_count, 2)
        self.mock_compare.assert_has_calls([
            call('https://twitch.tv', 'http://twitch.tv',
                 chat=self.channel, nick='botgotsthis', timestamp=self.now),
            call('http://megotsthis.com', 'https://twitch.tv',
                 chat=self.channel, nick='botgotsthis', timestamp=self.now),
            ])
        self.assertFalse(self.mock_handle.called)
        self.assertFalse(self.mock_except.called)

    def test_multiple_first_match(self):
        self.mock_followers.return_value = 1
        self.mock_compare.side_effect = [True, False]
        message = Message('https://twitch.tv megotsthis.com')
        self.response.geturl.side_effect = ['http://twitch.tv',
                                            'https://twitch.tv']
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.mock_request.assert_called_once_with(ANY)
        self.mock_compare.assert_called_once_with(
            'https://twitch.tv', 'http://twitch.tv',
            chat=self.channel, nick='botgotsthis', timestamp=self.now)
        self.mock_handle.assert_called_once_with(
            self.channel, 'botgotsthis', message)
        self.assertFalse(self.mock_except.called)

    def test_multiple_exception(self):
        self.mock_followers.return_value = 1
        message = Message('twitch.tv megotsthis.com twitch.tv')
        self.response.geturl.side_effect = [Exception,
                                            'https://twitch.tv',
                                            Exception]
        block_url.check_domain_redirect(self.channel, 'botgotsthis', message,
                                        self.now)
        self.mock_followers.assert_called_once_with('botgotsthis')
        self.mock_log.assert_called_once_with(ANY, ANY, self.now)
        self.assertEqual(self.mock_request.call_count, 3)
        self.assertEqual(self.response.geturl.call_count, 3)
        self.mock_compare.assert_called_once_with(
            'http://megotsthis.com', 'https://twitch.tv',
            chat=self.channel, nick='botgotsthis', timestamp=self.now)
        self.mock_except.assert_has_calls([call(ANY, ANY), call(ANY, ANY)])


class TestChannelBlockUrlCompareDomain(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.database = Mock(spec=DatabaseBase)
        self.message = Message('')
        self.now = datetime(2000, 1, 1)

        patcher = patch('source.public.channel.block_url.utils.logIrcMessage',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_log = patcher.start()

    def test(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv', 'http://twitch.tv',
                chat=self.channel, nick='botgotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)

    def test_different_domain(self):
        self.assertIs(
            block_url.compare_domains(
                'http://megotsthis.com', 'http://twitch.tv',
                chat=self.channel, nick='botgotsthis', timestamp=self.now),
            True)
        self.mock_log.assert_called_once_with(ANY, ANY, ANY)

    def test_different_page(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv/sda', 'http://twitch.tv/gamesdonequick',
                chat=self.channel, nick='botgotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)

    def test_different_query(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv/megotsthis?test',
                'http://twitch.tv/megotsthis?Kappa',
                chat=self.channel, nick='botgotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)

    def test_different_protocol(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv', 'https://twitch.tv',
                chat=self.channel, nick='botgotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)

    def test_different_subdomain(self):
        self.assertIs(
            block_url.compare_domains(
                'http://blog.twitch.tv', 'http://twitch.tv',
                chat=self.channel, nick='botgotsthis', timestamp=self.now),
            True)
        self.mock_log.assert_called_once_with(ANY, ANY, ANY)

    def test_different_subdomain_www(self):
        self.assertIs(
            block_url.compare_domains(
                'http://twitch.tv', 'https://www.twitch.tv',
                chat=self.channel, nick='botgotsthis', timestamp=self.now),
            False)
        self.assertFalse(self.mock_log.called)


class TestChannelBlockUrlHandleDifferentDomain(unittest.TestCase):
    def setUp(self):
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.channel.ircChannel = '#botgotsthis'
        self.database = Mock(spec=DatabaseBase)
        self.message = Message('')
        self.now = datetime(2000, 1, 1)

        patcher = patch('source.public.channel.block_url.factory.getDatabase',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_database = patcher.start()
        self.mock_database.return_value.__enter__.return_value = self.database

        patcher = patch('source.public.channel.block_url.timeout.timeout_user',
                        autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_timeout = patcher.start()

    def test(self):
        block_url.handle_different_domains(self.channel, 'botgotsthis',
                                           self.message)
        self.mock_database.assert_called_once_with()
        self.mock_timeout.assert_called_once_with(
            self.database, self.channel, 'botgotsthis', 'redirectUrl', 1, '')