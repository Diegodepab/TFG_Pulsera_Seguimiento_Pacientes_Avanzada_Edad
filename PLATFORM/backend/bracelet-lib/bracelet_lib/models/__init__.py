import time
import typing
import re
import databases
import sqlparse
import sqlalchemy as sa

from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.functions import ReturnTypeFromArgs


# noinspection PyPep8Naming
class unaccent_text(ReturnTypeFromArgs):
    pass


class DebugDatabases(databases.Database):
    # noinspection PyUnresolvedReferences
    def __init__(self, url: typing.Union[str, "DatabaseURL"], **options: typing.Any):
        super().__init__(url, **options)

    async def _print_execute(self, method: str, query: typing.Union[ClauseElement, str], values: typing.Dict = None):
        if isinstance(query, str):
            print(f'{method}: ', query)
            return

        compiled  = query.compile()
        query_str = str(compiled)

        for key, value in compiled.params.items():
            query_str = re.sub(r':{}(?!\d)'.format(key), str(value), query_str)

        print( sqlparse.format(query_str, reindent=True, keyword_case='upper') )

        start   = time.time()
        results = await getattr(super(), method)(query, values)
        elapsed = time.time() - start

        # noinspection PyUnresolvedReferences
        print( f'{method}: {elapsed * 1000:.5f} ms')

        return results

    async def execute(self, query: typing.Union[ClauseElement, str], values: typing.Dict = None) -> typing.Any:
        return await self._print_execute('execute', query, values)

    async def fetch_one(
        self, query: typing.Union[ClauseElement, str], values: typing.Dict = None
    ) -> typing.Optional[typing.Mapping]:
        return await self._print_execute('fetch_one', query, values)

    async def fetch_all(
        self, query: typing.Union[ClauseElement, str], values: typing.Dict = None
    ) -> typing.List[typing.Mapping]:
        return await self._print_execute('fetch_all', query, values)


class DatabaseManager:
    def __init__(self):
        self.__db_conn   : typing.Optional[databases.Database] = None
        self.__metadata  : sa.MetaData  = sa.MetaData()

    def init(self, db_url: str):
        """
        We need to initiate after creation so this is done with this method
        """
        self.__db_conn = databases.Database(db_url)

        # This can be enabled to debug SQL queries in console
        # self.__db_conn  = DebugDatabases(db_url)

        # If you want to populate the metadata inspecting the database uncomment this
        # engine = sa.create_engine(db_url, encoding='utf-8', pool_recycle=3600, pool_size=1)
        # self.__metadata.reflect(bind=engine)
        # engine.dispose()

    async def open(self):
        await self.__db_conn.connect()  # This can be managed too using context managers

    async def close(self):
        await self.__db_conn.disconnect()

    def get_db_conn(self) -> databases.Database:
        """
        Returns running db connection

        :return: databases.Database
        """
        assert self.__db_conn is not None, "You need to connect init() manager first"

        return self.__db_conn

    def get_metadata(self) -> sa.MetaData:
        """
        Returns SQL Alchemy metadata object

        :return: sa.MetaData
        """
        return self.__metadata


# "singleton"
database_manager = DatabaseManager()
