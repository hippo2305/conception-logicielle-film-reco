import os

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from utils.singleton import Singleton


class DBConnection(metaclass=Singleton):
    """
    Classe de connexion à la base de données
    (Singleton : une seule connexion)
    """

    def __init__(self):
        # Charge les variables d'environnement
        load_dotenv()
        load_dotenv(".env.local", override=True)

        required_vars = [
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_DATABASE",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_SCHEMA",
        ]

        missing = [v for v in required_vars if not os.getenv(v)]
        if missing:
            raise RuntimeError(
                "Variables d'environnement manquantes pour la DB : "
                + ", ".join(missing)
            )

        self.__connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT")),
            dbname=os.getenv("POSTGRES_DATABASE"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            options=f"-c search_path={os.getenv('POSTGRES_SCHEMA')}",
            cursor_factory=RealDictCursor,
        )

    @property
    def connection(self):
        return self.__connection
