from dao.init_db import init_db
from service.film_service import FilmService


def main():
    init_db()

    fs = FilmService()
    film = fs.import_from_tmdb("Inception", nb_acteurs=5)
    print(
        "Inséré :",
        film["id_film"],
        film["titre"],
        film["annee"],
        film["realisateur"],
        film["genres"],
        film["casting"],
    )


if __name__ == "__main__":
    main()
