from dao.db_connection import get_connection


class FilmDao:
    """
    Data Access Object for films.
    Handles persistence and retrieval of film data.
    """

    # -----------------------------
    # INSERT / UPDATE
    # -----------------------------
    def insert_film(self, film: dict) -> None:
        """
        Expected film dict:
        {
          "id_film": int,
          "titre": str,
          "annee": int | None,
          "realisateur": str | None,
          "genres": [str, ...],
          "casting": [str, ...]
        }
        """
        genres_str = ", ".join(film.get("genres", []))
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
                    film["id_film"],
                    film["titre"],
                    annee,
                    film.get("realisateur"),
                    genres_str,
                ),
            )

            # 2) Actors + casting relation
            for nom in film.get("casting", []):
                if not nom:
                    continue

                # Insert actor if not exists
                cur.execute(
                    """
                    INSERT INTO actor (nom)
                    VALUES (?)
                    ON CONFLICT(nom) DO NOTHING
                    """,
                    (nom,),
                )

                # Retrieve actor ID
                cur.execute(
                    "SELECT id_actor FROM actor WHERE nom = ?",
                    (nom,),
                )
                row = cur.fetchone()
                if not row:
                    continue

                id_actor = row["id_actor"]

                # Insert casting link
                cur.execute(
                    """
                    INSERT INTO casting (id_film, id_actor)
                    VALUES (?, ?)
                    ON CONFLICT(id_film, id_actor) DO NOTHING
                    """,
                    (film["id_film"], id_actor),
                )

    # -----------------------------
    # READ
    # -----------------------------
    def get_film(self, film_id: int) -> dict | None:
        """
        Retrieve a film by its ID.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM film WHERE id_film = ?",
                (film_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def get_film_by_title(self, title: str) -> dict | None:
        """
        Retrieve a film by its title (case-insensitive).
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT *
                FROM film
                WHERE LOWER(titre) = LOWER(?)
                LIMIT 1
                """,
                (title,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_films(self, exclude: int | None = None) -> list[dict]:
        """
        Retrieve all films, optionally excluding one by ID.
        """
        with get_connection() as conn:
            cur = conn.cursor()

            if exclude is not None:
                cur.execute(
                    "SELECT * FROM film WHERE id_film != ?",
                    (exclude,),
                )
            else:
                cur.execute("SELECT * FROM film")

            rows = cur.fetchall()
            return [dict(row) for row in rows]
