import os

from dotenv import load_dotenv
import requests


class TmdbService:
    """
    Service d'accès à l'API TMDB
    """

    def __init__(self):
        load_dotenv()
        load_dotenv(".env.local", override=True)

        self.api_key = os.getenv("TMDB_API_KEY")
        self.base_url = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")

        if not self.api_key:
            raise RuntimeError("Clé TMDB_API_KEY manquante")

    # -----------------------------
    # Recherche de films
    # -----------------------------
    def search_movie(self, query: str, page: int = 1) -> dict:
        url = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": query,
            "language": "fr-FR",
            "page": page,
        }

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    # -----------------------------
    # Détails d’un film
    # -----------------------------
    def movie_details(self, movie_id: int) -> dict:
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,
            "language": "fr-FR",
        }

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    # -----------------------------
    # Crédits (réalisateur + casting)
    # -----------------------------
    def movie_credits(self, movie_id: int) -> dict:
        url = f"{self.base_url}/movie/{movie_id}/credits"
        params = {"api_key": self.api_key}

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    # -----------------------------
    # Film filtré : id, titre, realisateur, genres, casting
    # -----------------------------
    def get_movie_filtered(self, query: str, nb_acteurs: int = 5) -> dict:
        search = self.search_movie(query=query, page=1)
        results = search.get("results", [])
        if not results:
            raise ValueError(f"Aucun film trouvé pour '{query}'")

        movie_id = results[0]["id"]

        details = self.movie_details(movie_id=movie_id)
        credits = self.movie_credits(movie_id=movie_id)

        realisateur = next(
            (
                c.get("name")
                for c in credits.get("crew", [])
                if c.get("job") == "Director"
            ),
            None,
        )

        casting = [
            a.get("name") for a in credits.get("cast", [])[:nb_acteurs] if a.get("name")
        ]

        genres = [g.get("name") for g in details.get("genres", []) if g.get("name")]

        return {
            "id_film": movie_id,
            "titre": details.get("title"),
            "realisateur": realisateur,
            "genres": genres,
            "casting": casting,
        }
