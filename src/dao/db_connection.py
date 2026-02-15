from contextlib import contextmanager
import os
import sqlite3

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from src.utils.singleton import Singleton


DB_PATH = "data/local.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

class DBConnection(metaclass=Singleton):
    """
    Classe de connexion à la base de données
    (Singleton : une seule connexion)
    """

    def __init__(self):
        load_dotenv(override=True)
        # Open the connection.
        if os.environ["POSTGRES"] == "False":
            self.__connection = get_connection()
        else:
            self.__connection = psycopg2.connect(
                host=os.environ["POSTGRES_HOST"],
                port=os.environ["POSTGRES_PORT"],
                database=os.environ["POSTGRES_DATABASE"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
                cursor_factory=RealDictCursor,
            )

    @property
    def connection(self):
        return self.__connection
