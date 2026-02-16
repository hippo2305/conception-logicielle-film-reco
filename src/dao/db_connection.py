from contextlib import contextmanager
import os
import sqlite3

from dotenv import load_dotenv
import psycopg2

from utils.singleton import Singleton


DB_PATH = "data/local.db"

class LocalDBConnection(metaclass=Singleton):
    """
    Classe de connexion à la base de données SQLite
    (Singleton : une seule connexion)
    """
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(DB_PATH)
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
    Classe de connexion à la base de données PostgreSQL
    (Singleton : une seule connexion)
    """
    def __init__(self):
        load_dotenv(override=True)
        self.__connection = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DATABASE"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )


    @property
    def connection(self):
        return self.__connection
