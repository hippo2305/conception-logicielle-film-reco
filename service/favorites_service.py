from dao.favorite_dao import FavoriteDao
from dao.film_dao import FilmDao
from service.tmdb_service import TmdbService


class FavoritesService:
    def __init__(self):
        self.tmdb = TmdbService()
        self.film_dao = FilmDao()
        self.fav_dao = FavoriteDao()

    def add_favorite_from_tmdb(
        self, user_id: int, movie_id: int, nb_acteurs: int = 5
    ) -> dict:
        # 1) Récupérer le film depuis TMDB
        film = self.tmdb.get_movie_full(movie_id=movie_id, nb_acteurs=nb_acteurs)

        # 2) Upsert en SQLite (film + actor + casting)
        self.film_dao.insert_film(film)

        # 3) Ajout favori
        self.fav_dao.add_favorite(user_id=user_id, film_id=film["id_film"])

        return film

    def remove_favorite(self, user_id: int, movie_id: int) -> None:
        self.fav_dao.remove_favorite(user_id=user_id, film_id=movie_id)
