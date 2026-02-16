from dao.db_connection import get_connection


class FavoriteDao:
    def add_favorite(self, user_id: int, film_id: int) -> None:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO favorites (id_user, id_film) VALUES (?, ?);",
                (user_id, film_id),
            )

    def remove_favorite(self, user_id: int, film_id: int) -> None:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM favorites WHERE id_user = ? AND id_film = ?;",
                (user_id, film_id),
            )

    def get_favorite_film_ids(self, user_id: int) -> set[int]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_film FROM favorites WHERE id_user = ?;", (user_id,))
            rows = cur.fetchall()
            return {int(r["id_film"]) for r in rows} if rows else set()

    def list_favorites(self, user_id: int) -> list[dict]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT f.*
                FROM film f
                JOIN favorites fav ON fav.id_film = f.id_film
                WHERE fav.id_user = ?
                ORDER BY fav.created_at DESC;
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows] if rows else []
