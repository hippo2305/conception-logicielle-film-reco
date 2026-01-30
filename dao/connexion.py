import os

import dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from utils.singleton import Singleton


class Connexion(metaclass=Singleton):
    """
    Classe de connexion à la base de données.
    Elle permet de n'ouvrir qu'une seule et unique connexion.
    """

    def __init__(self):
        """Ouverture de la connexion"""
        if hasattr(self, "_initialized") and self._initialized:
            return  # évite de réinitialiser si instance déjà créée

        dotenv.load_dotenv()

        self.__connection = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DATABASE"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            options=f"-c search_path={os.environ['POSTGRES_SCHEMA']}",
            cursor_factory=RealDictCursor,
        )

        self._initialized = True  # marque l'instance comme initialisée

    @property
    def connection(self):
        return self.__connection

    def close(self):
        if self.__connection:
            self.__connection.close()
            self.__connection = None
