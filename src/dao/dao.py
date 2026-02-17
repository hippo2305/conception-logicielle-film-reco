import os

from dotenv import load_dotenv

from src.dao.db_connection import DBConnection, LocalDBConnection


class DAO:
    def __init__(self):
        """
        Crée la BD si elle n'est pas créée
        """
        self.ordre_suppr_tables = ["FAVORIS", "CASTING", "ACTOR", "FILM", "USERS"]
        # Ordre logique de suppression pour respecter les contraintes FK
        query = """
            CREATE TABLE IF NOT EXISTS USERS (
                id_user SERIAL PRIMARY KEY,
                pseudo VARCHAR(255) NOT NULL,
                mdp VARCHAR(255) NOT NULL,
                UNIQUE(pseudo, mdp)
                );
                CREATE TABLE IF NOT EXISTS FILM (
                id_film SERIAL PRIMARY KEY,
                titre VARCHAR(255) NOT NULL,
                realisateur VARCHAR(255) NOT NULL,
                annee INT,
                genre VARCHAR(255) NOT NULL,
                UNIQUE(titre, realisateur)
                );
                CREATE TABLE IF NOT EXISTS ACTOR (
                id_actor SERIAL PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                prenom VARCHAR(255) NOT NULL,
                UNIQUE(nom, prenom)
                );
                CREATE TABLE IF NOT EXISTS FAVORIS (
                id_user INT NOT NULL,
                id_film INT NOT NULL,
                PRIMARY KEY (id_user, id_film),
                FOREIGN KEY (id_user) REFERENCES USERS(id_user) ON DELETE CASCADE,
                FOREIGN KEY (id_film) REFERENCES FILM(id_film) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS CASTING (
                id_film INT NOT NULL,
                id_actor INT NOT NULL,
                PRIMARY KEY (id_film, id_actor),
                FOREIGN KEY (id_film) REFERENCES FILM(id_film) ON DELETE CASCADE,
                FOREIGN KEY (id_actor) REFERENCES ACTOR(id_actor) ON DELETE CASCADE
                );
            """

        if self.postgres():
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        else:
            with LocalDBConnection().get_connection() as connection:
                cursor = connection.cursor()
                cursor.executescript(query.replace("SERIAL", "INTEGER"))
                connection.commit()

    def postgres(self):
        load_dotenv(override=True)
        if os.environ["POSTGRES"] == "False":
            return False
        elif os.environ["POSTGRES"] == "True":
            return True
        else:
            raise Exception(
                "La variable d'environnement POSTGRES n'accepte que deux valeurs : True et False"
            )

    def select_query(
        self, tablename, var="*", join=None, where=None, other=None, multiple=False
    ):
        query = f"SELECT {var} FROM {tablename}"
        if join:
            query += f" JOIN {join}"
        if where:
            query += f" WHERE {where}"
        if other:
            query += f" {other}"
        query += ";"

        if self.postgres():
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                if multiple:
                    return cursor.fetchall()
                else:
                    return cursor.fetchone()
        else:
            with LocalDBConnection().get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query)
                connection.commit()
                if multiple:
                    return cursor.fetchall()
                else:
                    return cursor.fetchone()

    def insert_query(self, tablename, vars, values, other=None):
        query = f"INSERT INTO {tablename} ({vars}) VALUES ({values})"
        if other:
            query += f" {other}"
        query += ";"

        if self.postgres():
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        else:
            with LocalDBConnection().get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query)
                connection.commit()

    def _del_data_table(self, nom_table: str | None = None) -> str | None:
        """
        Vide la table donnée en argument en majuscule
        Si aucune table n'est spécifiée, toutes les tables de la DB sont vidées
        """
        if nom_table in self.ordre_suppr_tables:
            query = f"DELETE FROM {nom_table};"
        if nom_table is None:
            query = ""
            for nom_table in self.ordre_suppr_tables:
                query += f"DELETE FROM {nom_table};"

        if self.postgres():
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                return True

        else:
            with LocalDBConnection().get_connection() as connection:
                cursor = connection.cursor()
                cursor.executescript(query)
                connection.commit()
                return True

    def _drop_table(self, nom_table: str | None = None) -> str | None:
        """
        Supprime la table donnée en argument en majuscule
        Si aucune table n'est spécifiée, toutes les tables de la DB sont supprimées
        """
        if nom_table in self.ordre_suppr_tables:
            query = f"DROP TABLE IF EXISTS {nom_table};"
        if nom_table is None:
            query = ""
            for nom_table in self.ordre_suppr_tables:
                query += f"DROP TABLE IF EXISTS {nom_table};"

        if self.postgres():
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                return True

        else:
            with LocalDBConnection().get_connection() as connection:
                cursor = connection.cursor()
                cursor.executescript(query)
                connection.commit()
                return True
