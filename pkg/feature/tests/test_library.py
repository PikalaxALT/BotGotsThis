import asynctest

import bot  # noqa: F401

from asynctest.mock import Mock, patch

from lib.cache import CacheStore
from lib.data.message import Message
from lib.helper import parser
from tests.unittest.mock_class import StrContains
from .. import library


def send(messages):
    pass


class TestFeatureLibrary(asynctest.TestCase):
    def setUp(self):
        self.data = Mock(spec=CacheStore)
        self.send = Mock(spec=send)

        patcher = patch('lib.items.feature')
        self.addCleanup(patcher.stop)
        self.mock_feature = patcher.start()
        self.mock_feature.features.return_value = {
            'feature': 'Feature',
            'none': None
            }

        patcher = patch('lib.helper.parser.get_response')
        self.addCleanup(patcher.stop)
        self.mock_response = patcher.start()

        patcher = patch(library.__name__ + '.feature_add')
        self.addCleanup(patcher.stop)
        self.mock_add = patcher.start()

        patcher = patch(library.__name__ + '.feature_remove')
        self.addCleanup(patcher.stop)
        self.mock_remove = patcher.start()

    async def test_add(self):
        self.mock_add.return_value = True
        self.mock_response.return_value = parser.Yes
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature feature'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.assertTrue(self.mock_response.called)
        self.mock_add.assert_called_once_with(
            self.data, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_remove.called)

    async def test_remove(self):
        self.mock_remove.return_value = True
        self.mock_response.return_value = parser.No
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature feature'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.assertTrue(self.mock_response.called)
        self.mock_remove.assert_called_once_with(
            self.data, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_add.called)

    async def test_not_existing_feature(self):
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature does_not_exist'),
                                  self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('feature', 'does_not_exist'))
        self.assertFalse(self.mock_response.called)
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)

    async def test_feature_none(self):
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature none'), self.send),
            True)
        self.send.assert_called_once_with(StrContains('feature', 'none'))
        self.assertFalse(self.mock_response.called)
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)

    async def test_bad_param(self):
        self.mock_response.return_value = parser.Unknown
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature feature Kappa'),
                                  self.send),
            True)
        self.send.assert_called_once_with(StrContains('parameter', 'kappa'))
        self.assertTrue(self.mock_response.called)
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)


class TestLibraryFeatureFeature_OLD(asynctest.TestCase):
    def setUp(self):
        self.data = Mock(spec=CacheStore)
        self.send = Mock(spec=send)

        patcher = patch('lib.items.feature')
        self.addCleanup(patcher.stop)
        self.mock_feature = patcher.start()
        self.mock_feature.features.return_value = {
            'feature': 'Feature',
            'none': None
            }

        patcher = patch(library.__name__ + '.feature_add')
        self.addCleanup(patcher.stop)
        self.mock_add = patcher.start()

        patcher = patch(library.__name__ + '.feature_remove')
        self.addCleanup(patcher.stop)
        self.mock_remove = patcher.start()

    async def test(self):
        self.mock_add.return_value = True
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature feature'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_add.assert_called_once_with(
            self.data, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_remove.called)

    async def test_add(self):
        self.mock_add.return_value = True
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature feature yes'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_add.assert_called_once_with(
            self.data, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_remove.called)

    async def test_remove(self):
        self.mock_remove.return_value = True
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature feature no'), self.send),
            True)
        self.assertFalse(self.send.called)
        self.mock_remove.assert_called_once_with(
            self.data, 'botgotsthis', 'feature', self.send)
        self.assertFalse(self.mock_add.called)

    async def test_not_existing_feature(self):
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature does_not_exist'),
                                  self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('feature', 'does_not_exist'))
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)

    async def test_feature_none(self):
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature none'), self.send),
            True)
        self.send.assert_called_once_with(StrContains('feature', 'none'))
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)

    async def test_bad_param(self):
        self.assertIs(
            await library.feature(self.data, 'botgotsthis',
                                  Message('!feature feature Kappa'),
                                  self.send),
            True)
        self.send.assert_called_once_with(StrContains('parameter', 'kappa'))
        self.assertFalse(self.mock_add.called)
        self.assertFalse(self.mock_remove.called)


class TestLibraryFeatureAdd(asynctest.TestCase):
    def setUp(self):
        self.data = Mock(spec=CacheStore)
        self.send = Mock(spec=send)

        patcher = patch('lib.items.feature')
        self.addCleanup(patcher.stop)
        self.mock_feature = patcher.start()
        self.mock_feature.features.return_value = {'feature': 'Feature'}

    async def test(self):
        self.data.hasFeature.return_value = False
        self.assertIs(
            await library.feature_add(self.data, 'botgotsthis', 'feature',
                                      self.send),
            True)
        self.send.assert_called_once_with(StrContains('Feature', 'enable'))
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.data.addFeature.assert_called_once_with(
            'botgotsthis', 'feature')

    async def test_existing(self):
        self.data.hasFeature.return_value = True
        self.assertIs(
            await library.feature_add(self.data, 'botgotsthis', 'feature',
                                      self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('Feature', 'already', 'enable'))
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.assertFalse(self.data.addFeature.called)


class TestLibraryFeatureRemove(asynctest.TestCase):
    def setUp(self):
        self.data = Mock(spec=CacheStore)
        self.send = Mock(spec=send)

        patcher = patch('lib.items.feature')
        self.addCleanup(patcher.stop)
        self.mock_feature = patcher.start()
        self.mock_feature.features.return_value = {'feature': 'Feature'}

    async def test(self):
        self.data.hasFeature.return_value = True
        self.assertIs(
            await library.feature_remove(self.data, 'botgotsthis',
                                         'feature', self.send),
            True)
        self.send.assert_called_once_with(StrContains('Feature', 'disable'))
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.data.removeFeature.assert_called_once_with(
            'botgotsthis', 'feature')

    async def test_existing(self):
        self.data.hasFeature.return_value = False
        self.assertIs(
            await library.feature_remove(self.data, 'botgotsthis',
                                         'feature', self.send),
            True)
        self.send.assert_called_once_with(
            StrContains('Feature', 'not', 'enable'))
        self.data.hasFeature.assert_called_once_with(
            'botgotsthis', 'feature')
        self.assertFalse(self.data.removeFeature.called)
