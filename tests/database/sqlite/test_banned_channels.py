import os

from tests.database.sqlite.test_database import TestSqlite
from lib import database
from tests.database.tests.banned_channels import TestBannedChannels


class TestSqliteBannedChannels(TestBannedChannels, TestSqlite):
    async def setUp(self):
        await super().setUp()
        sqlFile = os.path.join(
            os.path.dirname(database.__file__),
            'sqlite',
            'database.sql')
        with open(sqlFile) as f:
            await self.execute(f.read())
