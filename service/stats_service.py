from __future__ import annotations

from collections import Counter

from dao.db_connection import get_connection
from dao.film_dao import FilmDao


class StatsService:
    def __init__(self):
        self.film_dao = FilmDao()

    def top_favorited_films(self, limit: int = 10) -> list[dict]:
        """
        Renvoie les films les plus ajoutés en favoris.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT f.id_film, f.titre, f.annee, f.realisateur, f.genre,
                       COUNT(*) AS nb_favoris
                FROM favorites fav
                JOIN film f ON f.id_film = fav.id_film
                GROUP BY f.id_film
                ORDER BY nb_favoris DESC
                LIMIT ?;
                """,
                (limit,),
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows] if rows else []

    def favorites_by_genre(self) -> list[dict]:
        """
        Stat simple : nombre total de favoris par genre (approx car genres sont en texte).
        Exemple : si un film a "Action, Drama", il compte 1 pour Action et 1 pour Drama.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT f.genre
                FROM favorites fav
                JOIN film f ON f.id_film = fav.id_film;
                """
            )
            rows = cur.fetchall()

        counter = Counter()
        for r in rows or []:
            genre_str = r["genre"] or ""
            parts = [g.strip() for g in genre_str.split(",") if g.strip()]
            for g in parts:
                counter[g] += 1

        return [{"genre": k, "nb_favoris": v} for k, v in counter.most_common()]
