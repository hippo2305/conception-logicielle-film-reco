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

    def movie_details(self, movie_id: int) -> dict:
        url = f"{self.base_url}/movie/{movie_id}"
        params = {"api_key": self.api_key, "language": "fr-FR"}
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    def movie_credits(self, movie_id: int) -> dict:
        url = f"{self.base_url}/movie/{movie_id}/credits"
        params = {"api_key": self.api_key}
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    # -----------------------------
    # NOUVEAU : search "light" pour affichage
    # -----------------------------
    def search_movies_min(
        self, query: str, page: int = 1, limit: int = 20
    ) -> list[dict]:
        data = self.search_movie(query=query, page=page)
        results = data.get("results", []) or []
        out = []

        for r in results[:limit]:
            title = r.get("title") or r.get("name")
            release_date = r.get("release_date") or ""
            year = (
                int(release_date[:4])
                if release_date and len(release_date) >= 4
                else None
            )

            out.append(
                {
                    "id_film": r.get("id"),  # TMDB id
                    "titre": title,
                    "annee": year,
                    "overview": r.get("overview"),
                    "popularity": r.get("popularity"),
                }
            )
        return out

    # -----------------------------
    # NOUVEAU : film complet par ID
    # -----------------------------
    def get_movie_full(self, movie_id: int, nb_acteurs: int = 5) -> dict:
        details = self.movie_details(movie_id=movie_id)
        credits = self.movie_credits(movie_id=movie_id)

        realisateur = next(
            (
                c.get("name")
                for c in credits.get("crew", []) or []
                if c.get("job") == "Director"
            ),
            None,
        )

        casting = [
            a.get("name")
            for a in (credits.get("cast", []) or [])[:nb_acteurs]
            if a.get("name")
        ]

        genres = [
            g.get("name") for g in (details.get("genres", []) or []) if g.get("name")
        ]

        release_date = details.get("release_date") or ""
        annee = (
            int(release_date[:4]) if release_date and len(release_date) >= 4 else None
        )

        return {
            "id_film": int(details["id"]),
            "titre": details.get("title"),
            "realisateur": realisateur,
            "annee": annee,
            "genres": genres,
            "casting": casting,
        }
