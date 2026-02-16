import logging

from business_object.actor import Actor
from business_object.film import Film
from dao.dao import DAO
from dao.db_connection import DBConnection
from utils.log_decorator import log


class ActorDAO(DAO):
    """
    Cette classe permet d'interagir avec la table actor de la base de données.
    Elle gère l'ajout et la récupération des acteurs.
    """

    @log
    def exists(self, actor: Actor) -> bool:
        """
        Vérifie si un acteur existe déjà dans la base

        Paramètres
        ----------
        actor : Actor
            Objet Actor contenant :
            - nom
            - prenom

        Retour
        ------
        bool
            True si l'acteur est déjà présent, False sinon
        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM ACTOR WHERE nom = %(nom)s AND prenom = %(prenom)s;",
                    {"nom": actor.nom, "prenom": actor.prenom},
                )

                if cursor.fetchone() is None:
                    logging.info(
                        f"L'acteur {actor.prenom} {actor.nom} n'est pas présent dans la base."
                    )
                    return False
                else:
                    return True

        except Exception as e:
            logging.error(f"Erreur lors de la recherche de l'acteur : {e}")
            return False

    # -----------------------------
    # INSERTION
    # -----------------------------

    @log
    def add_actor(self, actor: Actor) -> bool:
        """
        Ajoute un acteur dans la table actor.

        Paramètres
        ----------
        actor : Actor
            Objet Actor contenant :
            - nom
            - prenom

        Retour
        ------
        bool
            True si insertion réussie, False sinon
        """
        try:
            if ActorDAO().exists(actor):
                logging.info(f"L'acteur {actor.prenom} {actor.nom} existe déjà.")
                return False
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ACTOR (nom, prenom)
                    VALUES (%(nom)s, %(prenom)s);
                    """,
                    {
                        "nom": actor.nom,
                        "prenom": actor.prenom,
                    },
                )
            connection.commit()
            return True

        except Exception as e:
            logging.error(f"Erreur lors de l'insertion de l'acteur : {e}")
            return False

    # -----------------------------
    # LECTURE
    # -----------------------------

    @log
    def get_id(self, actor: Actor) -> int:
        try:
            if not ActorDAO().exists(actor):
                logging.info(f"L'acteur {actor.prenom} {actor.nom} n'existe pas.")
                return True

            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id_actor
                    FROM ACTOR
                    WHERE nom = %(nom)s
                        AND prenom = %(prenom)s
                    LIMIT 1;
                    """,
                    {"nom": actor.nom, "prenom": actor.prenom},
                )

                connection.commit()
                return cursor.fetchone()["id_actor"]

        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'id : {e}")
            return None

    @log
    def get_all_actors(self) -> list[Actor]:
        """
        Retourne la liste de tous les acteurs.
        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute("SELECT * FROM ACTOR;")
                rows = cursor.fetchall()

        except Exception as e:
            logging.error(f"Erreur lors de la récupération des acteurs : {e}")
            return None

        return [self._row_to_actor(row) for row in rows] if rows else []

    @log
    def get_films(self, actor: Actor) -> list[Film]:
        """
        Récupère tous les films dans lesquel a joué un acteur
        """
        try:
            # Vérifie si le film existe
            if not self.exists(actor):
                logging.info(f"L'acteur {actor.prenom} {actor.nom} n'existe pas")
                return None

            # Récupère l'id de l'acteur
            id_actor = self.get_id(actor)

            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT f.id_film, f.titre, f.realisateur, f.genre
                    FROM FILM f
                    JOIN CASTING c ON c.id_film = f.id_film
                    WHERE c.id_actor = %(id_actor)s
                    ORDER BY f.titre ASC;
                    """,
                    {"id_actor": id_actor},
                )
                connection.commit()
                rows = cursor.fetchall()

        except Exception as e:
            logging.error(f"Erreur lors de la récupération du casting : {e}")
            return None

        return [self._row_to_film(row) for row in rows] if rows else None

    # -----------------------------
    # UTILITAIRE
    # -----------------------------
    def _row_to_film(self, row) -> Film:
        """
        Transforme une ligne SQL en objet Film.
        """
        film = Film(
            titre=row["titre"],
            realisateur=row["realisateur"],
            genre=row["genre"],
        )

        return film
