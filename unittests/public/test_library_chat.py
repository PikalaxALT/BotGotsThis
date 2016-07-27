import unittest
from bot.data import Channel
from bot.twitchmessage import IrcMessageTags
from datetime import datetime, timedelta
from source.data import ChatCommandArgs
from source.data.message import Message
from source.data.permissions import ChatPermissionSet
from source.database import DatabaseBase
from source.public.library import chat
from unittest.mock import MagicMock, Mock, PropertyMock, patch


class TestLibraryChat(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1)
        self.tags = IrcMessageTags()
        self.channel = Mock(spec=Channel)
        self.channel.channel = 'botgotsthis'
        self.database = Mock(spec=DatabaseBase)
        self.permissions = MagicMock(spec=ChatPermissionSet)
        self.args = ChatCommandArgs(self.database, self.channel, self.tags,
                                    'botgotsthis', Message(''),
                                    self.permissions, self.now)

    def test_send(self):
        self.assertIs(chat.send(self.channel), self.channel.send)
        chat.send(self.channel)('Kappa')
        self.channel.send.assert_called_once_with('Kappa')

    def test_send_priority(self):
        chat.sendPriority(self.channel, 0)('Kappa')
        self.channel.send.assert_called_once_with('Kappa', priority=0)

    def test_permission(self):
        self.permissions.__getitem__.return_value = True

        @chat.permission('')
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.permissions.__getitem__.assert_called_once_with('')

    def test_permission_not(self):
        self.permissions.__getitem__.return_value = False

        @chat.permission('')
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.permissions.__getitem__.assert_called_once_with('')

    def test_not_permission(self):
        self.permissions.__getitem__.return_value = False

        @chat.not_permission('')
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.permissions.__getitem__.assert_called_once_with('')

    def test_not_permission_not(self):
        self.permissions.__getitem__.return_value = True

        @chat.not_permission('')
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.permissions.__getitem__.assert_called_once_with('')

    def test_owner_channel(self):
        ownerProperty = PropertyMock(return_value=False)
        type(self.permissions).inOwnerChannel = ownerProperty

        @chat.ownerChannel
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        ownerProperty.assert_called_once_with()

    def test_owner_channel_not(self):
        ownerProperty = PropertyMock(return_value=False)
        type(self.permissions).inOwnerChannel = ownerProperty

        @chat.ownerChannel
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        ownerProperty.assert_called_once_with()

    def test_feature(self):
        self.database.hasFeature.return_value = True

        @chat.feature('')
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')

    def test_feature_not(self):
        self.database.hasFeature.return_value = False

        @chat.feature('')
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')

    def test_not_feature(self):
        self.database.hasFeature.return_value = False

        @chat.not_feature('')
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')

    def test_not_feature_not(self):
        self.database.hasFeature.return_value = True

        @chat.not_feature('')
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')

    def test_permission_feature(self):
        self.database.hasFeature.return_value = True
        self.permissions.__getitem__.return_value = True

        @chat.permission_feature(('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_called_once_with('')

    def test_permission_feature_not_permission(self):
        self.database.hasFeature.return_value = True
        self.permissions.__getitem__.return_value = False

        @chat.permission_feature(('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_permission_feature_not_feature(self):
        self.database.hasFeature.return_value = False
        self.permissions.__getitem__.return_value = True

        @chat.permission_feature(('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_permission_feature_not(self):
        self.database.hasFeature.return_value = False
        self.permissions.__getitem__.return_value = False

        @chat.permission_feature(('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_permission_feature_none_permission(self):
        self.database.hasFeature.return_value = True

        @chat.permission_feature((None, ''))
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_not_called()

    def test_permission_feature_none_feature(self):
        self.permissions.__getitem__.return_value = True

        @chat.permission_feature(('', None))
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_called_once_with('')

    def test_permission_feature_none_permission_not(self):
        self.database.hasFeature.return_value = False

        @chat.permission_feature((None, ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_not_called()

    def test_permission_feature_none_feature_not(self):
        self.permissions.__getitem__.return_value = False

        @chat.permission_feature(('', None))
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_called_once_with('')

    def test_permission_feature_none_permission_feature(self):
        @chat.permission_feature((None, None))
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_not_called()

    def test_permission_feature_multiple(self):
        self.database.hasFeature.side_effect = [False, True]
        self.permissions.__getitem__.side_effect = [False, True]

        @chat.permission_feature(('', ''), ('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), True)

    def test_permission_feature_multiple_not(self):
        self.database.hasFeature.side_effect = [False, True]
        self.permissions.__getitem__.side_effect = [True, False]

        @chat.permission_feature(('', ''), ('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_permission_not_feature(self):
        self.database.hasFeature.return_value = False
        self.permissions.__getitem__.return_value = True

        @chat.permission_not_feature(('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_called_once_with('')

    def test_permission_not_feature_not_permission(self):
        self.database.hasFeature.return_value = False
        self.permissions.__getitem__.return_value = False

        @chat.permission_not_feature(('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_permission_not_feature_not_feature(self):
        self.database.hasFeature.return_value = True
        self.permissions.__getitem__.return_value = True

        @chat.permission_not_feature(('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_permission_not_feature_not(self):
        self.database.hasFeature.return_value = True
        self.permissions.__getitem__.return_value = False

        @chat.permission_not_feature(('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_permission_not_feature_none_permission(self):
        self.database.hasFeature.return_value = False

        @chat.permission_not_feature((None, ''))
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_not_called()

    def test_permission_not_feature_none_feature(self):
        self.permissions.__getitem__.return_value = True

        @chat.permission_not_feature(('', None))
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_called_once_with('')

    def test_permission_not_feature_none_permission_not(self):
        self.database.hasFeature.return_value = True

        @chat.permission_not_feature((None, ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.database.hasFeature.assert_called_once_with('botgotsthis', '')
        self.permissions.__getitem__.assert_not_called()

    def test_permission_not_feature_none_feature_not(self):
        self.permissions.__getitem__.return_value = False

        @chat.permission_not_feature(('', None))
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_called_once_with('')

    def test_permission_not_feature_none_permission_feature(self):
        @chat.permission_not_feature((None, None))
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.database.hasFeature.assert_not_called()
        self.permissions.__getitem__.assert_not_called()

    def test_permission_not_feature_multiple(self):
        self.database.hasFeature.side_effect = [True, False]
        self.permissions.__getitem__.side_effect = [False, True]

        @chat.permission_not_feature(('', ''), ('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), True)

    def test_permission_not_feature_multiple_not(self):
        self.database.hasFeature.side_effect = [True, False]
        self.permissions.__getitem__.side_effect = [True, False]

        @chat.permission_not_feature(('', ''), ('', ''))
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    @patch('source.public.library.chat.inCooldown')
    def test_cooldown(self, mock_inCooldown):
        mock_inCooldown.return_value = False

        @chat.cooldown(timedelta(minutes=1), '')
        def t(args):
            return True
        self.assertIs(t(self.args), True)
        self.assertTrue(mock_inCooldown.called)

    @patch('source.public.library.chat.inCooldown')
    def test_cooldown_not(self, mock_inCooldown):
        mock_inCooldown.return_value = True

        @chat.cooldown(timedelta(minutes=1), '')
        def t(args):
            return True
        self.assertIs(t(self.args), False)
        self.assertTrue(mock_inCooldown.called)

    def test_in_cooldown(self):
        sessionData = {}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.inCooldown(self.args, timedelta(hours=1), ''), False)
        self.assertIn('', sessionData)
        self.assertEqual(sessionData[''], self.now)

    def test_in_cooldown_existing(self):
        sessionData = {'': self.now - timedelta(hours=1)}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.inCooldown(self.args, timedelta(hours=1), ''), False)
        self.assertIn('', sessionData)
        self.assertEqual(sessionData[''], self.now)

    def test_in_cooldown_recent(self):
        sessionData = {'': self.now - timedelta(seconds=1)}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.inCooldown(self.args, timedelta(hours=1), ''), True)
        self.assertIn('', sessionData)
        self.assertEqual(sessionData[''], self.now - timedelta(seconds=1))

    def test_in_cooldown_level_override(self):
        sessionData = {'': self.now - timedelta(seconds=1)}
        self.channel.sessionData = sessionData
        self.permissions.__getitem__.return_value = True
        self.assertIs(
            chat.inCooldown(self.args, timedelta(hours=1), '', ''), False)
        self.assertIn('', sessionData)
        self.assertEqual(sessionData[''], self.now)

    def test_in_user_cooldown(self):
        sessionData = {}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.in_user_cooldown(self.args, timedelta(hours=1), ''), False)
        self.assertIn('', sessionData)
        self.assertIn('botgotsthis', sessionData[''])
        self.assertEqual(sessionData['']['botgotsthis'], self.now)
        
    def test_in_user_cooldown_existing(self):
        sessionData = {'': {'botgotsthis': self.now - timedelta(hours=1)}}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.in_user_cooldown(self.args, timedelta(hours=1), ''), False)
        self.assertIn('', sessionData)
        self.assertIn('botgotsthis', sessionData[''])
        self.assertEqual(sessionData['']['botgotsthis'], self.now)

    def test_in_user_cooldown_recent(self):
        sessionData = {'': {'botgotsthis': self.now - timedelta(seconds=1)}}
        self.channel.sessionData = sessionData
        self.assertIs(
            chat.in_user_cooldown(self.args, timedelta(hours=1), ''), True)
        self.assertIn('', sessionData)
        self.assertIn('botgotsthis', sessionData[''])
        self.assertEqual(sessionData['']['botgotsthis'],
                         self.now - timedelta(seconds=1))

    def test_in_user_cooldown_level_override(self):
        sessionData = {'': {'botgotsthis': self.now - timedelta(seconds=1)}}
        self.channel.sessionData = sessionData
        self.permissions.__getitem__.return_value = True
        self.assertIs(
            chat.in_user_cooldown(self.args, timedelta(hours=1), '', ''),
            False)
        self.assertIn('', sessionData)
        self.assertIn('botgotsthis', sessionData[''])
        self.assertEqual(sessionData['']['botgotsthis'], self.now)

    def test_min_args(self):
        @chat.min_args(0)
        def t(args):
            return True
        self.assertIs(t(self.args), True)

    def test_min_args_not_enough(self):
        @chat.min_args(1)
        def t(args):
            return True
        self.assertIs(t(self.args), False)

    def test_min_args_not_return(self):
        @chat.min_args(1, _return=True)
        def t(args):
            return False
        self.assertIs(t(self.args), True)

    def test_min_args_not_reason(self):
        @chat.min_args(1, reason='Kappa')
        def t(args):
            return False
        t(self.args)
        self.channel.send.assert_called_once_with('Kappa')