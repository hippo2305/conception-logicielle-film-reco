import logging

from business_object.actor import Actor
from business_object.film import Film
from dao.actor_dao import ActorDAO
from dao.dao import DAO
from dao.db_connection import DBConnection
from utils.log_decorator import log


class FilmDAO(DAO):
    """
        Cette classe permet d'intéragir essentiellement avec la table film de la base de
        données. Dispose de méthodes pour ajouter et retourner des films selon des filtres.
    """
    @log
    def exists(self, film: Film) -> bool:
        """
        Vérifie si un film existe déjà dans la base

        Paramètres
        ----------
        film : Film
            Objet Film contenant :
            - titre
            - realisateur
            - genre

        Retour
        ------
        bool
            True si le film est déjà présent, False sinon
        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM FILM WHERE titre = %(titre)s AND realisateur = %(realisateur)s;",
                    {
                        "titre": film.titre,
                        "realisateur": film.realisateur
                    },
                )

                if cursor.fetchone() is None:
                    logging.info(
                        f"Le film {film.titre} n'est pas présent dans la base."
                    )
                    return False
                else:
                    return True

        except Exception as e:
            logging.error(f"Erreur lors de la recherche de l'acteur : {e}")
            return False

    @log
    def add_film(self, film: Film) -> bool:
        """
        Ajoute un film dans la table film de la base de données.

        Paramètres
        ----------
        film : Film
            Objet Film contenant :
            - titre
            - realisateur
            - genre

        Retour
        ------
        bool
            True si insertion réussie, False sinon
        """

        try:
            # Vérifie si le film existe déjà
            if self.exists(film):
                logging.info(
                    f"Le film {film.titre} existe déjà."
                )
                return False

            # Insertion du film
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO FILM (titre, realisateur, genre)
                    VALUES (%(titre)s, %(realisateur)s, %(genre)s);
                    """,
                    {
                        "titre": film.titre,
                        "realisateur": film.realisateur,
                        "genre": film.genre,
                    },
                )

                connection.commit()
                return True

        except Exception as e:
            logging.error(f"Erreur lors de l'insertion du film : {e}")
            return False

    @log
    def add_casting(self, film: Film) -> bool:
        """
        Ajoute le casting d'un film dans la BDD et ajoute les associations
        """
        try:
            id_film = FilmDAO().get_id(film)

            # Ajout des acteurs si non présents dans la BDD et récupération des id
            if film.casting:
                for actor in film.casting:
                    # N'ajout l'acteur que s'il n'est pas déjà dans la BDD
                    if not ActorDAO().exists(actor):
                        ActorDAO().add_actor(actor)
                    id_actor = ActorDAO().get_id(actor)

                    # Insertion dans la table d'association
                    with DBConnection().connection as connection, connection.cursor() as cursor:
                        # /!\ À AJOUTER : vérification que l'association n'existe pas déjà

                        cursor.execute(
                            """
                            INSERT INTO CASTING (id_film, id_actor)
                            VALUES (%(id_film)s, %(id_actor)s)
                            """,
                            {
                                "id_film": id_film,
                                "id_actor": id_actor
                            }
                        )
                        connection.commit()
                return True

            else:
                logging.info(
                    f"Le casting du film {film.titre} n'est pas renseigné."
                )

        except Exception as e:
            logging.error(f"Erreur lors de l'ajout du casting' : {e}")
            return None

    @log
    def get_id(self, film: Film) -> int:
        """
        Récupère l'id d'un film dans la BDD
        """
        try:
            # Vérifie si le film existe
            if not self.exists(film):
                logging.info(
                    f"Le film {film.titre} n'existe pas"
                )
                return None

            # Récupération de l'id
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                                """
                                    SELECT id_film
                                    FROM FILM
                                    WHERE titre = %(titre)s
                                        AND realisateur = %(realisateur)s
                                    LIMIT 1;
                                """,
                                {
                                    "titre": film.titre,
                                    "realisateur": film.realisateur,
                                }
                            )

                connection.commit()
                return cursor.fetchone()["id_film"]

        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'id : {e}")
            return None

    @log
    def get_all_films(self) -> list[Film]:
        """
        Retourne la liste des films contenus dans la base de données.
        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute("SELECT * FROM FILM;")
                connection.commit()
                rows = cursor.fetchall()

        except Exception as e:
            logging.info(e)
            raise

        films = []
        if rows:
            print(rows)
            for row in rows:
                films.append(
                    Film(
                        titre=row["titre"],
                        realisateur=row["realisateur"],
                        genre=row["genre"],
                    )
                )
        return films

    @log
    def get_casting(self, film: Film) -> list[Actor]:
        try:
            # Vérifie si le film existe
            if not self.exists(film):
                logging.info(
                    f"Le film {film.titre} n'existe pas"
                )
                return None

            # Récupère l'id du film
            id_film = self.get_id(film)

            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.id_actor, a.nom, a.prenom
                    FROM ACTOR a
                    JOIN CASTING c ON c.id_actor = a.id_actor
                    WHERE c.id_film = %(id_film)s
                    ORDER BY a.nom ASC;
                    """,
                    {"id_film": id_film},
                )
                connection.commit()
                rows = cursor.fetchall()

        except Exception as e:
            logging.error(f"Erreur lors de la récupération du casting : {e}")
            return None

        return [self._row_to_actor(row) for row in rows] if rows else None

    '''
    @log
    def get_by_user(self, user) -> list[Film]:
        """
        Retourne les films associés à un utilisateur.
        Hypothèse : table de liaison aime(id_user, id_film).
        """
        # On accepte un objet User (user.id_user) ou directement l'id (str/int)
        id_user = getattr(user, "id_user", user)

        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT f.titre, f.realisateur, f.genre
                    FROM film f
                    JOIN aime a ON a.id_film = f.id_film
                    WHERE a.id_user = %(id_user)s
                    ORDER BY f.titre ASC;
                    """,
                    {"id_user": id_user},
                )
                rows = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        return [self._row_to_film(r) for r in rows] if rows else []
    '''

    # -----------------------------
    # LISTES DISTINCTES (filtres)
    # -----------------------------
    @log
    def genre_list(self) -> list[str]:
        """Retourne la liste des genres enregistrés en base."""
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT UPPER(genre) AS genre FROM FILM;")
                res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        return [row["genre"] for row in res] if res else []

    @log
    def director_list(self) -> list[str]:
        """Retourne la liste des réalisateurs enregistrés en base."""
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT UPPER(realisateur) AS realisateur FROM FILM;")
                res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        return [row["realisateur"] for row in res] if res else []

    @log
    def list_id(self) -> list[str]:
        """Retourne la liste des identifiants des films existants en base."""
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT id_film FROM film;")
                res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        return [row["id_film"] for row in res] if res else []

    @log
    def get_by_id(self, id_film: str) -> Film | None:
        """Trouve un film à partir de son identifiant."""
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM FILM
                    WHERE id_film = %(id_film)s;
                    """,
                    {"id_film": id_film},
                )
                res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        if not res:
            return None

        return Film(
            titre=res["titre"],
            realisateur=res["realisateur"],
            genre=res["genre"],
        )

    @log
    def get_by_genre(self, genre: str) -> list[Film]:
        """Trouve les films selon un genre donné (insensible à la casse)."""
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM FILM
                    WHERE LOWER(genre) = LOWER(%(genre)s);
                    """,
                    {"genre": genre},
                )
                res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        films = []
        if res:
            for row in res:
                films.append(
                    Film(
                        titre=row["titre"],
                        realisateur=row["realisateur"],
                        genre=row["genre"],
                    )
                )
        return films

    @log
    def get_by_director(self, realisateur: str) -> list[Film]:
        """Trouve les films selon un réalisateur donné (insensible à la casse)."""
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM FILM
                    WHERE LOWER(realisateur) = LOWER(%(realisateur)s);
                    """,
                    {"realisateur": realisateur},
                )
                res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        films = []
        if res:
            for row in res:
                films.append(
                    Film(
                        titre=row["titre"],
                        realisateur=row["realisateur"],
                        genre=row["genre"],
                    )
                )
        return films

    @log
    def get_by_title(self, titre: str) -> list[Film]:
        """
        Trouve des films dont le titre contient une chaîne (recherche partielle).
        Compatible PostgreSQL avec ILIKE (insensible à la casse).
        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM FILM
                    WHERE titre ILIKE %(pattern)s
                    ORDER BY titre ASC;
                    """,
                    {"pattern": f"%{titre}%"},
                )
                res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        films = []
        if res:
            for row in res:
                films.append(
                    Film(
                        titre=row["titre"],
                        realisateur=row["realisateur"],
                        genre=row["genre"],
                    )
                )
        return films

    # -----------------------------
    # UTILITAIRE
    # -----------------------------
    def _row_to_actor(self, row) -> Actor:
        """
        Transforme une ligne SQL en objet Actor.
        """
        return Actor(
            nom=row["nom"],
            prenom=row["prenom"],
        )
