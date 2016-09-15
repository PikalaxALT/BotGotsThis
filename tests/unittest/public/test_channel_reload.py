from unittest.mock import patch

from source.public.channel import reload
from tests.unittest.base_channel import TestChannel
from tests.unittest.mock_class import PartialMatch


class TestChannelFeature(TestChannel):
    @patch('source.public.library.reload.full_reload', autospec=True)
    def test_reload(self, mock_reload):
        self.assertIs(reload.commandReload(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(reload.commandReload(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))

    @patch('source.public.library.reload.reload_commands', autospec=True)
    def test_reload_commands(self, mock_reload):
        self.assertIs(reload.commandReloadCommands(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(reload.commandReloadCommands(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))

    @patch('source.public.library.reload.reload_config', autospec=True)
    def test_reload_config(self, mock_reload):
        self.assertIs(reload.commandReloadConfig(self.args), False)
        self.assertFalse(mock_reload.called)
        mock_reload.return_value = True
        self.permissions.inOwnerChannel = True
        self.permissionSet['owner'] = True
        self.assertIs(reload.commandReloadConfig(self.args), True)
        mock_reload.assert_called_once_with(
            PartialMatch(self.channel.send, priority=0))