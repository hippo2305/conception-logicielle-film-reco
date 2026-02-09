# import logging

# from business_object.film import Film
# from dao.db_connection import DBConnection
# from utils.log_decorator import log
# from utils.singleton import Singleton


# class FilmDao(metaclass=Singleton):
#     """
#     Cette classe permet d'intéragir essentiellement avec la table film de la base de
#     données. Dispose de méthodes pour ajouter et retourner des films selon des filtres.
#     """

#     @log
#     def add_film(self, film: Film) -> bool:
#         """
#         Ajoute un film dans la table film de la base de données.

#         Paramètres
#         ----------
#         film : Film
#             Objet Film contenant :
#             - id_film
#             - titre
#             - realisateur
#             - genre

#         Retour
#         ------
#         bool
#             True si insertion réussie, False sinon
#         """

#         try:
#             with DBConnection().connection as connection:
#                 with connection.cursor() as cursor:
#                     # Vérifie si le film existe déjà
#                     cursor.execute(
#                         "SELECT 1 FROM film WHERE id_film = %(id_film)s;",
#                         {"id_film": film.id_film},
#                     )

#                     if cursor.fetchone() is not None:
#                         logging.info(
#                             f"Le film avec id_film={film.id_film} existe déjà."
#                         )
#                         return False

#                     # Insertion du film
#                     cursor.execute(
#                         """
#                         INSERT INTO film (id_film, titre, realisateur, genre)
#                         VALUES (%(id_film)s, %(titre)s, %(realisateur)s, %(genre)s);
#                         """,
#                         {
#                             "id_film": film.id_film,
#                             "titre": film.titre,
#                             "realisateur": film.realisateur,
#                             "genre": film.genre,
#                         },
#                     )

#                 connection.commit()
#                 return True

#         except Exception as e:
#             logging.error(f"Erreur lors de l'insertion du film : {e}")
#             return False

#     @log
#     def get_all_films(self) -> list[Film]:
#         """
#         Retourne la liste des films contenus dans la base de données.
#         """
#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute("SELECT * FROM film;")
#                 rows = cursor.fetchall()

#         except Exception as e:
#             logging.info(e)
#             raise

#         films = []
#         if rows:
#             for row in rows:
#                 films.append(
#                     Film(
#                         id_film=row["id_film"],
#                         titre=row["titre"],
#                         realisateur=row["realisateur"],
#                         genre=row["genre"],
#                     )
#                 )
#         return films

#     @log
#     def get_films_by_user(self, user) -> list[Film]:
#         """
#         Retourne les films associés à un utilisateur.
#         Hypothèse : table de liaison aime(id_user, id_film).
#         """
#         # On accepte un objet User (user.id_user) ou directement l'id (str/int)
#         id_user = getattr(user, "id_user", user)

#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute(
#                     """
#                     SELECT f.id_film, f.titre, f.realisateur, f.genre
#                     FROM film f
#                     JOIN aime a ON a.id_film = f.id_film
#                     WHERE a.id_user = %(id_user)s
#                     ORDER BY f.titre ASC;
#                     """,
#                     {"id_user": id_user},
#                 )
#                 rows = cursor.fetchall()
#         except Exception as e:
#             logging.info(e)
#             raise

#         return [self._row_to_film(r) for r in rows] if rows else []

#     @log
#     def get_films_by_actor(self, actor) -> list[Film]:
#         """
#         Retourne les films dans lesquels joue un acteur.
#         Hypothèse : table casting(id_film, id_actor).
#         """
#         id_actor = getattr(actor, "id_actor", actor)

#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute(
#                     """
#                     SELECT f.id_film, f.titre, f.realisateur, f.genre
#                     FROM film f
#                     JOIN casting c ON c.id_film = f.id_film
#                     WHERE c.id_actor = %(id_actor)s
#                     ORDER BY f.titre ASC;
#                     """,
#                     {"id_actor": id_actor},
#                 )
#                 rows = cursor.fetchall()
#         except Exception as e:
#             logging.info(e)
#             raise

#         return [self._row_to_film(r) for r in rows] if rows else []

#     # -----------------------------
#     # LISTES DISTINCTES (filtres)
#     # -----------------------------
#     @log
#     def genre_list(self) -> list[str]:
#         """Retourne la liste des genres enregistrés en base."""
#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute("SELECT DISTINCT UPPER(genre) AS genre FROM film;")
#                 res = cursor.fetchall()
#         except Exception as e:
#             logging.info(e)
#             raise

#         return [row["genre"] for row in res] if res else []

#     @log
#     def director_list(self) -> list[str]:
#         """Retourne la liste des réalisateurs enregistrés en base."""
#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute(
#                     "SELECT DISTINCT UPPER(realisateur) AS realisateur FROM film;"
#                 )
#                 res = cursor.fetchall()
#         except Exception as e:
#             logging.info(e)
#             raise

#         return [row["realisateur"] for row in res] if res else []

#     @log
#     def list_id_film(self) -> list[str]:
#         """Retourne la liste des identifiants des films existants en base."""
#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute("SELECT DISTINCT id_film FROM film;")
#                 res = cursor.fetchall()
#         except Exception as e:
#             logging.info(e)
#             raise

#         return [row["id_film"] for row in res] if res else []

#     @log
#     def get_by_id(self, id_film: str) -> Film | None:
#         """Trouve un film à partir de son identifiant."""
#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute(
#                     """
#                         SELECT * FROM film
#                         WHERE id_film = %(id_film)s;
#                         """,
#                     {"id_film": id_film},
#                 )
#                 res = cursor.fetchone()
#         except Exception as e:
#             logging.info(e)
#             raise

#         if not res:
#             return None

#         return Film(
#             id_film=res["id_film"],
#             titre=res["titre"],
#             realisateur=res["realisateur"],
#             genre=res["genre"],
#         )

#     @log
#     def get_by_genre(self, genre: str) -> list[Film]:
#         """Trouve les films selon un genre donné (insensible à la casse)."""
#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute(
#                     """
#                         SELECT * FROM film
#                         WHERE LOWER(genre) = LOWER(%(genre)s);
#                         """,
#                     {"genre": genre},
#                 )
#                 res = cursor.fetchall()
#         except Exception as e:
#             logging.info(e)
#             raise

#         films = []
#         if res:
#             for row in res:
#                 films.append(
#                     Film(
#                         id_film=row["id_film"],
#                         titre=row["titre"],
#                         realisateur=row["realisateur"],
#                         genre=row["genre"],
#                     )
#                 )
#         return films

#     @log
#     def get_by_director(self, realisateur: str) -> list[Film]:
#         """Trouve les films selon un réalisateur donné (insensible à la casse)."""
#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute(
#                     """
#                         SELECT * FROM film
#                         WHERE LOWER(realisateur) = LOWER(%(realisateur)s);
#                         """,
#                     {"realisateur": realisateur},
#                 )
#                 res = cursor.fetchall()
#         except Exception as e:
#             logging.info(e)
#             raise

#         films = []
#         if res:
#             for row in res:
#                 films.append(
#                     Film(
#                         id_film=row["id_film"],
#                         titre=row["titre"],
#                         realisateur=row["realisateur"],
#                         genre=row["genre"],
#                     )
#                 )
#         return films

#     @log
#     def get_by_title(self, titre: str) -> list[Film]:
#         """
#         Trouve des films dont le titre contient une chaîne (recherche partielle).
#         Compatible PostgreSQL avec ILIKE (insensible à la casse).
#         """
#         try:
#             with DBConnection().connection as connection, connection.cursor() as cursor:
#                 cursor.execute(
#                     """
#                         SELECT * FROM film
#                         WHERE titre ILIKE %(pattern)s
#                         ORDER BY titre ASC;
#                         """,
#                     {"pattern": f"%{titre}%"},
#                 )
#                 res = cursor.fetchall()
#         except Exception as e:
#             logging.info(e)
#             raise

#         films = []
#         if res:
#             for row in res:
#                 films.append(
#                     Film(
#                         id_film=row["id_film"],
#                         titre=row["titre"],
#                         realisateur=row["realisateur"],
#                         genre=row["genre"],
#                     )
#                 )
#         return films
