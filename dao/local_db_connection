import duckdb

from utils.singleton import Singleton


class LocalDBConnection(metaclass=Singleton):
    """
    Technical class to open only one connection to the DB.
    """

    def __init__(self):
        self.__connection = duckdb.connect("dao/local.db")

    @property
    def connection(self):
        """
        return the opened connection.

        :return: the opened connection.
        """
        return self.__connection
