import logging

from business_object.actor import Actor
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class ActorDao(metaclass=Singleton):
    """
    Cette classe permet d'interagir avec la table actor de la base de données.
    Elle gère l'ajout et la récupération des acteurs.
    """

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
            - id_actor
            - nom
            - prenom
            - age

        Retour
        ------
        bool
            True si insertion réussie, False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Vérifie si l'acteur existe déjà
                    cursor.execute(
                        "SELECT 1 FROM actor WHERE id_actor = %(id_actor)s;",
                        {"id_actor": actor.id_actor},
                    )

                    if cursor.fetchone() is not None:
                        logging.info(
                            f"L'acteur avec id_actor={actor.id_actor} existe déjà."
                        )
                        return False

                    cursor.execute(
                        """
                        INSERT INTO actor (id_actor, nom, prenom, age)
                        VALUES (%(id_actor)s, %(nom)s, %(prenom)s, %(age)s);
                        """,
                        {
                            "id_actor": actor.id_actor,
                            "nom": actor.nom,
                            "prenom": actor.prenom,
                            "age": actor.age,
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
    def get_all_actors(self) -> list[Actor]:
        """
        Retourne la liste de tous les acteurs.
        """
        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute("SELECT * FROM actor;")
                rows = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        return [self._row_to_actor(row) for row in rows] if rows else []

    @log
    def get_actor_by_film(self, film) -> list[Actor]:
        """
        Retourne les acteurs jouant dans un film donné.
        Hypothèse : table de jointure casting(id_film, id_actor).
        """
        id_film = getattr(film, "id_film", film)

        try:
            with DBConnection().connection as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.id_actor, a.nom, a.prenom, a.age
                    FROM actor a
                    JOIN casting c ON c.id_actor = a.id_actor
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

    # -----------------------------
    # UTILITAIRE
    # -----------------------------
    def _row_to_actor(self, row) -> Actor:
        """
        Transforme une ligne SQL en objet Actor.
        """
        return Actor(
            id_actor=row["id_actor"],
            nom=row["nom"],
            prenom=row["prenom"],
            age=row["age"],
            films=[],
        )
