# from db_connection import DBConnection


# class DAO:
#     def __init__(self):
#         """
#         Crée la BD si elle n'est pas créée
#         """
#         self.ordre_suppr_tables = ["ACTEUR", "FILMS", "USER"]
#         # Ordre logique de suppression pour respecter les contraintes FK
#         with DBConnection().connection as connection, connection.cursor() as cursor:
#             cursor.execute("""
#                 CREATE SEQUENCE IF NOT EXISTS id_sequence START 1;
#                 CREATE TABLE IF NOT EXISTS USER (
#                 id_user INTEGER PRIMARY KEY DEFAULT nextval('id_sequence'),
#                 pseudo VARCHAR(255) NOT NULL UNIQUE,
#                 mdp VARCHAR(255) NOT NULL
#                 );
#                 CREATE TABLE IF NOT EXISTS FILMS (
#                 id_films INTEGER PRIMARY KEY DEFAULT nextval('id_sequence'),
#                 titre VARCHAR(255) NOT NULL,
#                 realisateur VARCHAR(255) NOT NULL,
#                 annee INT,
#                 genre VARCHAR(255) NOT NULL,
#                 UNIQUE(titre, realisateur)
#                 );
#                 CREATE TABLE IF NOT EXISTS ACTOR (
#                 id_actor INTEGER PRIMARY KEY DEFAULT nextval('id_sequence'),
#                 nom VARCHAR(255) NOT NULL,
#                 prenom VARCHAR(255) NOT NULL,
#                 age INTEGER,
#                 UNIQUE(nom, prenom)
#                 );
#                 """)

#     def _del_data_table(self, nom_table: str | None = None) -> str | None:
#         """
#         Vide la table donnée en argument en majuscule
#         Si aucune table n'est spécifiée, toutes les tables de la DB sont vidées
#         """
#         with DBConnection().connection as connection, connection.cursor() as cursor:
#             if nom_table in self.ordre_suppr_table:
#                 cursor.execute(f"DELETE FROM {nom_table};")
#                 connection.commit()
#                 return "table vidée"
#             if nom_table is None:
#                 for nom_table in self.ordre_suppr_table:
#                     cursor.execute(f"DELETE FROM {nom_table};")
#                 connection.commit()
#                 return "tables vidées"

#     def _drop_table(self, nom_table: str | None = None) -> str | None:
#         """
#         Supprime la table donnée en argument en majuscule
#         Si aucune table n'est spécifiée, toutes les tables de la DB sont supprimées
#         """
#         with DBConnection().connection as connection, connection.cursor() as cursor:
#             if nom_table in self.ordre_suppr_tables:
#                 cursor.execute(f"DROP TABLE IF EXISTS {nom_table} CASCADE;")
#                 connection.commit()
#                 return "table supprimée"
#             if nom_table is None:
#                 for table in self.ordre_suppr_tables:
#                     cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
#                 connection.commit()
#                 return "tables supprimées"
