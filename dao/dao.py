from abc import ABC

from dao.local_db_connection import LocalDBConnection
import duckdb


class DAO(ABC):
    def __init__(self):
        """
        Crée la BD si elle n'est pas créée
        """
        with LocalDBConnection().connection as connection:
            connection.sql("""
                CREATE TABLE IF NOT EXISTS USER (
                id SERIAL PRIMARY KEY,
                pseudo VARCHAR(255) NOT NULL UNIQUE,
                mdp VARCHAR(255) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS FILMS (
                id SERIAL PRIMARY KEY,
                titre VARCHAR(255) NOT NULL,
                realisateur VARCHAR(255) NOT NULL,
                annee INT,
                genre VARCHAR(255) NOT NULL,
                UNIQUE(titre, realisateur)
                );
                CREATE TABLE IF NOT EXISTS FILMS (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                prenom VARCHAR(255) NOT NULL,
                UNIQUE(nom, prenom)
                );
                """)

    def query_csv_file(self, path: str, select: str, where=None):
        query = f"""
            SELECT {select}
            FROM read_csv('{path}')
        """
        if where is not None:
            query += f"WHERE {where}"
        res = duckdb.sql(query)
        return res


#    def add_database_from_csv(self, path: str, table: str):
#        with LocalDBConnection().connection as connection:
#
#            connection.sql(f"INSERT INTO {table} VALUES {ligne}")
#
#    def query_data_base():
#        pass


if __name__ == "__main__":
    print(DAO().query_csv_file("data/csv/user.csv", "*"))
