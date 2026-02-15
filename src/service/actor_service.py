from business_object.actor import Actor
from business_object.film import Film
from dao.actor_dao import ActorDao


class ActorService:
    """
    Service métier pour la gestion des acteurs.
    """

    def __init__(self):
        self._actor_dao = ActorDao()

    # -----------------------------
    # Instanciation
    # -----------------------------
    def instantiate_actor(
        self,
        id_actor: int,
        nom: str,
        prenom: str,
        age: int,
    ) -> Actor:
        """
        Crée et retourne un objet Actor.
        """
        return Actor(
            id_actor=id_actor,
            nom=nom,
            prenom=prenom,
            age=age,
            films=[],
        )

    # -----------------------------
    # Films joués
    # -----------------------------
    def add_films(self, actor: Actor, film: Film) -> bool:
        """
        Ajoute un film à la filmographie d’un acteur.
        """
        if film not in actor.films:
            actor.films.append(film)
            return True
        return False

    def get_films(self, actor: Actor) -> list[Film]:
        """
        Retourne les films dans lesquels joue l’acteur.
        """
        return actor.films

    # -----------------------------
    # Persistance
    # -----------------------------
    def save_actor(self, actor: Actor) -> bool:
        """
        Sauvegarde l’acteur en base de données.
        """
        return self._actor_dao.add_actor(actor)
