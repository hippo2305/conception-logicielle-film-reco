from src.service.tmdb_service import TmdbService


res2 = TmdbService().get_movie_filtered("Titanic")

print(res2.titre)
