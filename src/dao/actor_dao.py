import logging

from src.business_object.actor import Actor
from src.business_object.film import Film
from src.dao.dao import DAO
from src.utils.log_decorator import log


class ActorDAO:
    """
    Cette classe permet d'interagir avec la table actor de la base de données.
    Elle gère l'ajout et la récupération des acteurs.
    """

    def __init__(self):
        self.dao = DAO()

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
            res = self.dao.select_query(
                "ACTOR", "1", where=f"nom = '{actor.nom}' AND prenom = '{actor.prenom}'"
            )

            if res is None:
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
            if self.exists(actor):
                logging.info(f"L'acteur {actor.prenom} {actor.nom} existe déjà.")
                return False

            self.dao.insert_query(
                "ACTOR", "nom, prenom", f"'{actor.nom}', '{actor.prenom}'"
            )
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

            res = self.dao.select_query(
                "ACTOR",
                "id_actor",
                where=f"nom = '{actor.nom}' AND prenom = '{actor.prenom}'",
                other="LIMIT 1",
            )
            return res[0]

        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'id : {e}")
            return None

    @log
    def get_all_actors(self) -> list[Actor]:
        """
        Retourne la liste de tous les acteurs.
        """
        try:
            rows = self.dao.select_query("ACTOR", multiple=True)

        except Exception as e:
            logging.error(f"Erreur lors de la récupération des acteurs : {e}")
            return None

        return [Actor(row[1], row[2]) for row in rows] if rows else []

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

            rows = self.dao.select_query(
                "FILM f",
                "f.id_film, f.titre, f.realisateur, f.annee, f.genre",
                "CASTING c ON c.id_film = f.id_film",
                f"c.id_actor = {id_actor}",
                "ORDER BY f.titre ASC",
                multiple=True,
            )

        except Exception as e:
            logging.error(f"Erreur lors de la récupération des films : {e}")
            return None

        return [Film(row[1], row[2], row[3], row[4]) for row in rows] if rows else None
