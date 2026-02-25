from dao.db_connection import get_connection


class FilmDao:
    """
    DAO SQLite - table film (+ actor + casting via insert_film).
    """

    def insert_film(self, film: dict) -> None:
        """
        film dict attendu:
        {
          "id_film": int,
          "titre": str,
          "annee": int | None,
          "realisateur": str | None,
          "genres": [str, ...],
          "casting": [str, ...]
        }
        """
        if not film or film.get("id_film") is None or not film.get("titre"):
            raise ValueError("Film invalide (id_film/titre manquant)")

        genres_str = ", ".join([g for g in (film.get("genres") or []) if g])
        annee = film.get("annee")

        with get_connection() as conn:
            cur = conn.cursor()

            # 1) Film (UPSERT)
            cur.execute(
                """
                INSERT INTO film (id_film, titre, annee, realisateur, genre)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id_film) DO UPDATE SET
                    titre = excluded.titre,
                    annee = excluded.annee,
                    realisateur = excluded.realisateur,
                    genre = excluded.genre
                """,
                (
                    int(film["id_film"]),
                    film["titre"],
                    annee,
                    film.get("realisateur"),
                    genres_str,
                ),
            )

            # 2) Actors + casting relation
            for nom in film.get("casting") or []:
                nom = (nom or "").strip()
                if not nom:
                    continue

                cur.execute(
                    """
                    INSERT INTO actor (nom)
                    VALUES (?)
                    ON CONFLICT(nom) DO NOTHING
                    """,
                    (nom,),
                )

                cur.execute("SELECT id_actor FROM actor WHERE nom = ?", (nom,))
                row = cur.fetchone()
                if not row:
                    continue

                id_actor = int(row["id_actor"])

                cur.execute(
                    """
                    INSERT INTO casting (id_film, id_actor)
                    VALUES (?, ?)
                    ON CONFLICT(id_film, id_actor) DO NOTHING
                    """,
                    (int(film["id_film"]), id_actor),
                )

    def get_film_by_id(self, id_film: int) -> dict | None:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM film WHERE id_film = ?;", (id_film,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_film_by_title(self, title: str, annee: int | None = None) -> dict | None:
        title = (title or "").strip()
        if not title:
            return None

        with get_connection() as conn:
            cur = conn.cursor()

            if annee is None:
                cur.execute(
                    """
                    SELECT *
                    FROM film
                    WHERE LOWER(titre) = LOWER(?)
                    LIMIT 1
                    """,
                    (title,),
                )
            else:
                cur.execute(
                    """
                    SELECT *
                    FROM film
                    WHERE LOWER(titre) = LOWER(?) AND annee = ?
                    LIMIT 1
                    """,
                    (title, annee),
                )

            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_films(self, exclude: int | None = None) -> list[dict]:
        with get_connection() as conn:
            cur = conn.cursor()

            if exclude is not None:
                cur.execute("SELECT * FROM film WHERE id_film != ?;", (exclude,))
            else:
                cur.execute("SELECT * FROM film;")

            rows = cur.fetchall()
            return [dict(row) for row in rows] if rows else []
