from src.dao.db_connection import DBConnection


class DAO:
    def __init__(self):
        """
        Crée la BD si elle n'est pas créée
        """
        self.ordre_suppr_tables = ["FAVORIS", "CASTING", "ACTOR", "FILM", "USERS"]
        # Ordre logique de suppression pour respecter les contraintes FK
        with DBConnection().connection as connection, connection.cursor() as cursor:
            cursor.execute("""
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
                """)
            connection.commit()

    def _del_data_table(self, nom_table: str | None = None) -> str | None:
        """
        Vide la table donnée en argument en majuscule
        Si aucune table n'est spécifiée, toutes les tables de la DB sont vidées
        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            if nom_table in self.ordre_suppr_table:
                cursor.execute(f"DELETE FROM {nom_table};")
                connection.commit()
                return "table vidée"
            if nom_table is None:
                for nom_table in self.ordre_suppr_table:
                    cursor.execute(f"DELETE FROM {nom_table};")
                connection.commit()
                return "tables vidées"

    def _drop_table(self, nom_table: str | None = None) -> str | None:
        """
        Supprime la table donnée en argument en majuscule
        Si aucune table n'est spécifiée, toutes les tables de la DB sont supprimées
        """
        with DBConnection().connection as connection, connection.cursor() as cursor:
            if nom_table in self.ordre_suppr_tables:
                cursor.execute(f"DROP TABLE IF EXISTS {nom_table} CASCADE;")
                connection.commit()
                return "table supprimée"
            if nom_table is None:
                for table in self.ordre_suppr_tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                connection.commit()
                return "tables supprimées"
