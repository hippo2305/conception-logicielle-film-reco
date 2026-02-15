from src.business_object.actor import Actor
from src.business_object.film import Film
from src.dao.film_dao import FilmDAO
from src.service.tmdb_service import TmdbService


class FilmService:
    """
    Service métier pour la gestion des films.
    """

    def __init__(self):
        self.tmdb = TmdbService()
        self.dao = FilmDAO()

    def import_from_tmdb(self, query: str, nb_acteurs: int = 5) -> dict:
        film = self.tmdb.get_movie_filtered(query=query, nb_acteurs=nb_acteurs)
        self.dao.insert_film(film)
        return film

    # -----------------------------
    # Instanciation
    # -----------------------------
    def instantiate_film(
        self,
        titre: str,
        realisateur: str,
        genre: str,
    ) -> Film:
        """
        Crée et retourne un objet Film.
        """
        return Film(
            titre=titre,
            realisateur=realisateur,
            genre=genre,
        )

    # -----------------------------
    # Casting
    # -----------------------------
    def add_casting(self, film: Film, casting: list[Actor]) -> bool:
        """
        Ajoute le casting aux attributs d'un film.
        """
        if not film.casting:
            film.casting = []

        for actor in casting:
            if actor not in film.casting:
                film.casting.append(actor)
            else:
                return False
        return True

    def get_casting(self, film: Film) -> list[Actor]:
        """
        Retourne le casting du film.
        """
        return film.casting

    # -----------------------------
    # Persistance
    # -----------------------------
    def save_film(self, film: Film) -> bool:
        """
        Sauvegarde le film en base de données.
        """
        self._film_dao.add_film(film)

        if film.casting:
            self._film_dao.add_casting(film)

        return True
