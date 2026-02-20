from __future__ import annotations

from dao.film_dao import FilmDao


class RecommendationService:
    """
    Recommandations simples, sans ML :
    - par titre : films dont le titre contient la requête
    - par genre : films dont le champ 'genre' contient le genre
    - si l'utilisateur choisit un film : recommander par genres du film
    """

    def __init__(self):
        self.film_dao = FilmDao()

    def recommend_by_title(self, query: str, limit: int = 10) -> list[dict]:
        query = (query or "").strip().lower()
        if not query:
            return []

        films = self.film_dao.get_all_films() or []
        res = [f for f in films if query in (f.get("titre") or "").lower()]
        return res[:limit]

    def recommend_by_genre(self, genre: str, limit: int = 10) -> list[dict]:
        genre = (genre or "").strip().lower()
        if not genre:
            return []

        films = self.film_dao.get_all_films() or []
        res = [f for f in films if genre in (f.get("genre") or "").lower()]
        return res[:limit]

    def recommend_from_film(self, id_film: int, limit: int = 10) -> list[dict]:
        film = self.film_dao.get_film_by_id(id_film)
        if not film:
            return []

        # genres stockés comme "Action, Drama" etc.
        genre_str = (film.get("genre") or "").lower()
        genres = [g.strip() for g in genre_str.split(",") if g.strip()]
        if not genres:
            return []

        films = self.film_dao.get_all_films() or []

        # même genre que le film choisi, mais exclure le film lui-même
        def matches_any_genre(f: dict) -> bool:
            fg = (f.get("genre") or "").lower()
            return any(g in fg for g in genres)

        res = [f for f in films if f.get("id_film") != id_film and matches_any_genre(f)]
        return res[:limit]
