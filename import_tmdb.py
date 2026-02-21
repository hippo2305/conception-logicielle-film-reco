from dao.init_db import init_db
from service.film_service import FilmService


def main():
    init_db()

    fs = FilmService()

    titres = [
        "Titanic",
        "Inception",
        "Interstellar",
        "The Dark Knight",
        "Avatar",
        "Gladiator",
        "The Matrix",
        "Forrest Gump",
        "The Shawshank Redemption",
        "The Godfather",
        "Pulp Fiction",
        "Fight Club",
        "The Lord of the Rings: The Fellowship of the Ring",
        "The Lord of the Rings: The Two Towers",
        "The Lord of the Rings: The Return of the King",
        "Star Wars: Episode IV - A New Hope",
        "Jurassic Park",
        "The Lion King",
        "The Prestige",
        "Parasite",
    ]

    for titre in titres:
        try:
            film = fs.import_from_tmdb(titre, nb_acteurs=5)
            print(
                "Inséré :",
                film["id_film"],
                film["titre"],
                film["annee"],
                film["realisateur"],
                film["genres"],
                film["casting"],
            )
        except Exception as e:
            print(f"Erreur pour {titre} :", e)


if __name__ == "__main__":
    main()
