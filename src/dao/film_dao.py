from dao.db_connection import get_connection


class FilmDao:
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
        genres_str = ", ".join(film.get("genres", []))
        annee = film.get("annee")

        with get_connection() as conn:
            cur = conn.cursor()

            # 1) film (UPSERT)
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

            # 2) acteurs + liaison casting
            for nom in film.get("casting", []):
                if not nom:
                    continue

                # Insert actor si n'existe pas
                cur.execute(
                    """
                    INSERT INTO actor (nom)
                    VALUES (?)
                    ON CONFLICT(nom) DO NOTHING
                    """,
                    (nom,),
                )

                # Récupérer id_actor
                cur.execute(
                    "SELECT id_actor FROM actor WHERE nom = ?",
                    (nom,),
                )
                row = cur.fetchone()
                if not row:
                    continue

                id_actor = row["id_actor"]

                # Insert lien casting
                cur.execute(
                    """
                    INSERT INTO casting (id_film, id_actor)
                    VALUES (?, ?)
                    ON CONFLICT(id_film, id_actor) DO NOTHING
                    """,
                    (film["id_film"], id_actor),
                )
