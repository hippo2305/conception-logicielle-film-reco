import logging

from business_object.actor import Actor
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
                    {
                        "nom": actor.nom,
                        "prenom": actor.prenom
                    },
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
                logging.info(
                    f"L'acteur {actor.prenom} {actor.nom} existe déjà."
                )
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
    def get_actor_id(self, actor: Actor) -> int:
        try:
            if not ActorDAO().exists(actor):
                logging.info(
                    f"L'acteur {actor.prenom} {actor.nom} n'existe pas."
                )
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
                    {
                        "nom": actor.nom,
                        "prenom": actor.prenom
                    }
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
            logging.info(e)
            raise

        return [self._row_to_actor(row) for row in rows] if rows else []

    '''
    @log
    def get_actor_films:
    '''

    ''' ÉQUIVAUT À FilmDAO().get_film_casting() - Problème d'importation circulaire
    @log
    def get_actors_by_film(self, film) -> list[Actor]:
        """
        Retourne les acteurs jouant dans un film donné.
        Hypothèse : table de jointure casting(id_film, id_actor).
        """
        id_film = FilmDAO().get_film_id(film)

        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.id_actor, a.nom, a.prenom, a.age
                    FROM ACTOR a
                    JOIN CASTING c ON c.id_actor = a.id_actor
                    WHERE c.id_film = %(id_film)s
                    ORDER BY a.nom ASC;
                    """,
                    {"id_film": id_film},
                )
                rows = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        return [self._row_to_actor(row) for row in rows] if rows else []
    '''

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
