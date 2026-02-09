from dao.dao_film import FilmDao
from service.tmdb_service import TmdbService


class FilmService:
    def __init__(self):
        self.tmdb = TmdbService()
        self.dao = FilmDao()

    def import_from_tmdb(self, query: str, nb_acteurs: int = 5) -> dict:
        film = self.tmdb.get_movie_filtered(query=query, nb_acteurs=nb_acteurs)
        self.dao.insert_film(film)
        return film
