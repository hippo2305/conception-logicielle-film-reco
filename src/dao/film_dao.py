import logging

from business_object.actor import Actor
from business_object.film import Film
from dao.actor_dao import ActorDAO
from dao.dao import DAO
from utils.log_decorator import log


class FilmDAO:
    """
    Cette classe permet d'intéragir essentiellement avec la table film de la base de
    données. Dispose de méthodes pour ajouter et retourner des films selon des filtres.
    """
    def __init__(self):
        self.dao = DAO()
        self.actor_dao = ActorDAO()

    '''
    def insert_film(self, film: dict) -> None:
        """
        film dict attendu:
        {
          "id_film": int,
          "titre": str,
          "annee": int | None,
          "realisateur": str | None,
          "genres": [str, ...],
          "casting": [str, ...]
        }
        """
        genres_str = ", ".join(film.get("genres", []))
        annee = film.get("annee")

        with DBConnection().connection as connection, connection.cursor() as cur:

            # 1) film (UPSERT)
            cur.execute(
                """
                INSERT INTO film (id_film, titre, annee, realisateur, genre)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id_film) DO UPDATE SET
                    titre = excluded.titre,
                    annee = excluded.annee,
                    realisateur = excluded.realisateur,
                    genre = excluded.genre
                """,
                (
                    film["id_film"],
                    film["titre"],
                    annee,
                    film.get("realisateur"),
                    genres_str,
                ),
            )

            # 2) acteurs + liaison casting
            for nom in film.get("casting", []):
                if not nom:
                    continue

                # Insert actor si n'existe pas
                cur.execute(
                    """
                    INSERT INTO actor (nom)
                    VALUES (?)
                    ON CONFLICT(nom) DO NOTHING
                    """,
                    (nom,),
                )

                # Récupérer id_actor
                cur.execute(
                    "SELECT id_actor FROM actor WHERE nom = ?",
                    (nom,),
                )
                row = cur.fetchone()
                if not row:
                    continue

                id_actor = row["id_actor"]

                # Insert lien casting
                cur.execute(
                    """
                    INSERT INTO casting (id_film, id_actor)
                    VALUES (?, ?)
                    ON CONFLICT(id_film, id_actor) DO NOTHING
                    """,
                    (film["id_film"], id_actor),
                )
    '''

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
            res = self.dao.select_query("FILM", "1", where = f"titre = '{film.titre}' AND realisateur = '{film.realisateur}'")
            if res is None:
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
            - annee
            - genre

        Retour
        ------
        bool
            True si insertion réussie, False sinon
        """

        try:
            # Vérifie si le film existe déjà
            if self.exists(film):
                logging.info(f"Le film {film.titre} existe déjà.")
                return False

            # Insertion du film
            self.dao.insert_query("FILM", "titre, realisateur, annee, genre", f"'{film.titre}', '{film.realisateur}', '{film.annee}', '{film.genre}'")

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
                    if not self.actor_dao.exists(actor):
                        self.actor_dao.add_actor(actor)
                    id_actor = self.actor_dao.get_id(actor)

                    # Insertion dans la table d'association
                    self.dao.insert_query("CASTING", "id_film, id_actor", f"{id_film}, {id_actor}")
                    # /!\ À AJOUTER : vérification que l'association n'existe pas déjà

                return True

            else:
                logging.info(f"Le casting du film {film.titre} n'est pas renseigné.")

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
                logging.info(f"Le film {film.titre} n'existe pas")
                return None

            # Récupération de l'id
            res = self.dao.select_query("FILM", "id_film", where = f"titre = '{film.titre}' AND realisateur = '{film.realisateur}'")
            return res[0]

        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'id : {e}")
            return None

    @log
    def get_all_films(self) -> list[Film]:
        """
        Retourne la liste des films contenus dans la base de données.
        """
        try:
            rows = self.dao.select_query("FILM", multiple = True)

        except Exception as e:
            logging.info(e)
            raise

        films = []
        if rows:
            print(rows)
            for row in rows:
                films.append(
                    Film(
                        titre=row[1],
                        realisateur=row[2],
                        annee=row[3],
                        genre=row[4]
                    )
                )
        return films

    @log
    def get_casting(self, film: Film) -> list[Actor]:
        try:
            # Vérifie si le film existe
            if not self.exists(film):
                logging.info(f"Le film {film.titre} n'existe pas")
                return None

            # Récupère l'id du film
            id_film = self.get_id(film)

            rows = self.dao.select_query(
                "ACTOR a", "a.id_actor, a.nom, a.prenom",
                "CASTING c on c.id_actor = a.id_actor",
                f"c.id_film = {id_film}",
                "ORDER BY a.nom ASC",
                multiple = True,
            )

        except Exception as e:
            logging.error(f"Erreur lors de la récupération du casting : {e}")
            return None

        return [Actor(row[1], row[2]) for row in rows] if rows else None

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
        res = self.dao.select_query("FILM", "DISTINCT UPPER(genre) AS genre", multiple = True)

        return [row[0] for row in res] if res else []

    @log
    def director_list(self) -> list[str]:
        """Retourne la liste des réalisateurs enregistrés en base."""
        try:
            res = self.dao.select_query("FILM", "DISTINCT UPPER(realisateur) AS realisateur", multiple = True)
        except Exception as e:
            logging.info(e)
            raise

        return [row[2] for row in res] if res else []

    @log
    def list_id(self) -> list[str]:
        """Retourne la liste des identifiants des films existants en base."""
        try:
            res = self.dao.select_query("FILM", "DISTINCT id_film", multiple = True)
        except Exception as e:
            logging.info(e)
            raise

        return [row[0] for row in res] if res else []

    @log
    def get_by_id(self, id_film: str) -> Film | None:
        """Trouve un film à partir de son identifiant."""
        try:
            res = self.dao.select_query("FILM", where = f"id_film = {id_film}")

        except Exception as e:
            logging.info(e)
            raise

        if not res:
            return None

        return Film(
            titre=res[1],
            realisateur=res[2],
            annee=res[3],
            genre=res[4],
        )

    @log
    def get_by_genre(self, genre: str) -> list[Film]:
        """Trouve les films selon un genre donné (insensible à la casse)."""
        try:
            res = self.dao.select_query("FILM", where = f"LOWER(genre) = LOWER({genre})", multiple = True)

        except Exception as e:
            logging.info(e)
            raise

        films = []
        if res:
            for row in res:
                films.append(
                    Film(
                        titre=row[1],
                        realisateur=row[2],
                        annee=row[3],
                        genre=row[4],
                    )
                )
        return films

    @log
    def get_by_director(self, realisateur: str) -> list[Film]:
        """Trouve les films selon un réalisateur donné (insensible à la casse)."""
        try:
            res = self.dao.select_query("FILM", where = f"LOWER(realisateur) = LOWER({realisateur})", multiple = True)

        except Exception as e:
            logging.info(e)
            raise

        films = []
        if res:
            for row in res:
                films.append(
                    Film(
                        titre=row[1],
                        realisateur=row[2],
                        annee=row[3],
                        genre=row[4],
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
            res = self.dao.select_query("FILM", where = f"titre ILIKE {titre}", multiple = True)

        except Exception as e:
            logging.info(e)
            raise

        films = []
        if res:
            for row in res:
                films.append(
                    Film(
                        titre=row[1],
                        realisateur=row[2],
                        annee=row[3],
                        genre=row[4]
                    )
                )
        return films
