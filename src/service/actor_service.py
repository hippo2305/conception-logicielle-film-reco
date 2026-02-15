from src.business_object.actor import Actor
from src.business_object.film import Film
from src.dao.actor_dao import ActorDAO


class ActorService:
    """
    Service métier pour la gestion des acteurs.
    """

    def __init__(self):
        self._actor_dao = ActorDAO()

    # -----------------------------
    # Instanciation
    # -----------------------------
    def instantiate_actor(
        self,
        nom: str,
        prenom: str,
    ) -> Actor:
        """
        Crée et retourne un objet Actor.
        """
        return Actor(
            nom=nom,
            prenom=prenom,
        )

    # -----------------------------
    # Films joués
    # -----------------------------
    def get_films(self, actor: Actor) -> list[Film]:
        """
        Retourne les films dans lesquels joue l'acteur.
        """
        return self._actor_dao.get_films(actor)

    # -----------------------------
    # Persistance
    # -----------------------------
    def save_actor(self, actor: Actor) -> bool:
        """
        Sauvegarde l'acteur en base de données.
        """
        return self._actor_dao.add_actor(actor)
