import os

from tests.database.postgres.test_database import TestPostgres
from lib import database
from tests.database.tests.auto_join import TestAutoJoin


class TestPostgresAutoJoin(TestAutoJoin, TestPostgres):
    async def setUp(self):
        await super().setUp()
        sqlFile = os.path.join(
            os.path.dirname(database.__file__),
            'postgres',
            'database.sql')
        with open(sqlFile) as f:
            await self.execute(f.read())
