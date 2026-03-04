from pathlib import Path

from src.dao.db_connection import DBConnection, LocalDBConnection


SCHEMA_PATH = Path(__file__).parent / "schema.sql"

class InitDB:
    def get_schema(self, path) -> str:
        with open(path, encoding="utf-8") as f:
            schema = f.read()
        return schema

    def init_db(self) -> None:
        query = self.get_schema(SCHEMA_PATH)

        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()

    def init_localdb(self) -> None:
        query = self.get_schema(SCHEMA_PATH)

        with LocalDBConnection().get_connection() as connection:
            cursor = connection.cursor()
            cursor.executescript(query.replace("SERIAL", "INTEGER"))
            connection.commit()
