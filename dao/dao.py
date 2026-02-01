import duckdb


class DAO:
    def __init__(self):
        """
        Crée la BD si elle n'est pas créée
        """
        self.ordre_suppr_tables = ["ACTEUR", "FILMS", "USER"]
        # Ordre logique de suppression pour respecter les contraintes FK
        with duckdb.connect("data/local.db") as connection:
            connection.sql("""
                CREATE SEQUENCE IF NOT EXISTS id_sequence START 1;
                CREATE TABLE IF NOT EXISTS USER (
                id INTEGER PRIMARY KEY DEFAULT nextval('id_sequence'),
                pseudo VARCHAR(255) NOT NULL UNIQUE,
                mdp VARCHAR(255) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS FILMS (
                id INTEGER PRIMARY KEY DEFAULT nextval('id_sequence'),
                titre VARCHAR(255) NOT NULL,
                realisateur VARCHAR(255) NOT NULL,
                annee INT,
                genre VARCHAR(255) NOT NULL,
                UNIQUE(titre, realisateur)
                );
                CREATE TABLE IF NOT EXISTS ACTEUR (
                id INTEGER PRIMARY KEY DEFAULT nextval('id_sequence'),
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
        res = duckdb.sql(query).fetchall()
        return res

    def get_csv_headers(self, path: str):
        query = f"""
            SELECT *
            FROM read_csv('{path}',
                header = false)
            LIMIT 1;
        """
        res = duckdb.sql(query).fetchone()
        return res

    def add_database_from_csv(self, path: str, table: str):
        columns = str(DAO().get_csv_headers(path)).replace("'", "")
        with duckdb.connect("data/local.db") as connection:
            for line in DAO().query_csv_file(path, "*"):
                connection.sql(f"INSERT INTO {table} {columns} VALUES {line}")

    def query_data_base(self, table: str, select: str, where=None):
        query = f"""
            SELECT {select}
            FROM {table}
        """
        if where is not None:
            query += f"WHERE {where}"
        with duckdb.connect("data/local.db") as connection:
            res = connection.sql(query).fetchall()
        return res

    def _del_data_table(self, nom_table: str | None = None) -> str | None:
        """
        Vide la table donnée en argument en majuscule
        Si aucune table n'est spécifiée, toutes les tables de la DB sont vidées
        """
        with duckdb.connect("data/local.db") as connection:
            if nom_table in self.ordre_suppr_table:
                connection.sql(f"DELETE FROM {nom_table};")
                return "table vidée"
            if nom_table is None:
                for nom_table in self.ordre_suppr_table:
                    connection.sql(f"DELETE FROM {nom_table};")
                return "tables vidées"

    def _drop_table(self, nom_table: str | None = None) -> str | None:
        """
        Supprime la table donnée en argument en majuscule
        Si aucune table n'est spécifiée, toutes les tables de la DB sont supprimées
        """
        with duckdb.connect("data/local.db") as connection:
            if nom_table in self.ordre_suppr_tables:
                connection.sql(f"DROP TABLE IF EXISTS {nom_table} CASCADE;")
                return "table supprimée"
            if nom_table is None:
                for table in self.ordre_suppr_tables:
                    connection.sql(f"DROP TABLE IF EXISTS {table} CASCADE;")
                return "tables supprimées"
