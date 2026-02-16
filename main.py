import os

from dotenv import load_dotenv

from service.recommendation_service import RecommendationService


class MAIN:
    @staticmethod
    def load_env() -> None:
        load_dotenv()
        if os.path.exists(".env"):
            load_dotenv(".env", override=True)


if __name__ == "__main__":
    MAIN.load_env()

    reco = RecommendationService()
    results = reco.recommend_similar_movies_by_title(
        reference_title="Titanic",
        top_k=5,
    )

    for movie in results:
        print(movie["titre"], "-", movie["annee"])
