from dao.film_dao import FilmDao


def parse_genres(genres_str: str) -> list[str]:
    if not genres_str:
        return []
    return [g.strip().lower() for g in genres_str.split(",")]


class RecommendationService:
    """
    Service responsible for computing movie recommendations.
    """

    def __init__(self):
        self.film_dao = FilmDao()

    def recommend_similar_movies_by_title(
        self, reference_title: str, top_k: int = 5
    ) -> list[dict]:
        """
        Recommend movies similar to a reference movie given its title.
        """
        reference_movie = self.film_dao.get_film_by_title(reference_title)

        if not reference_movie:
            raise ValueError(f"Movie '{reference_title}' not found in database")

        reference_id = reference_movie["id_film"]

        candidate_movies = self.film_dao.get_all_films(exclude=reference_id)

        reference_genres = set(parse_genres(reference_movie["genre"]))

        scored_movies: list[tuple[int, dict]] = []

        for movie in candidate_movies:
            score = 0
            movie_genres = set(parse_genres(movie["genre"]))

            # Genre similarity
            score += 2 * len(reference_genres & movie_genres)

            # Same director
            if (
                movie["realisateur"]
                and reference_movie["realisateur"]
                and movie["realisateur"] == reference_movie["realisateur"]
            ):
                score += 3

            # Release year proximity
            if (
                movie["annee"]
                and reference_movie["annee"]
                and abs(movie["annee"] - reference_movie["annee"]) <= 5
            ):
                score += 1

            scored_movies.append((score, movie))

        scored_movies.sort(key=lambda x: x[0], reverse=True)

        return [movie for score, movie in scored_movies[:top_k]]
