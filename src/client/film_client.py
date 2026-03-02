from src.service.film_service import FilmService
from src.service.tmdb_service import TmdbService


class FilmClient:
    def __init__(self):
        self.film_service = FilmService()
        self.tmdb_service = TmdbService()

    def get_film_tmdb(self, titre):
        film = self.tmdb_service.get_movie_filtered(titre)

        return {
            "titre" : film.titre,
            "realisateur" : film.realisateur,
        }
