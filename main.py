import os

from dotenv import load_dotenv

from service.tmdb_service import TmdbService


class MAIN:
    @staticmethod
    def load_env() -> None:
        load_dotenv()
        local_env_path = ".env"
        if os.path.exists(local_env_path):
            load_dotenv(dotenv_path=local_env_path, override=True)

    @staticmethod
    def get_local_env(mask_secrets: bool = True) -> dict[str, str]:
        # Charge aussi .env.local si présent
        local_env_path = ".env"
        if os.path.exists(local_env_path):
            load_dotenv(dotenv_path=local_env_path)

        env = dict(os.environ)

        if mask_secrets:
            keyword_mask = [
                "password",
                "pwd",
                "jeton",
                "token",
                "bearer",
                "secret",
                "key",
                "cle",
                "mdp",
                "motdepasse",
            ]
            for k in list(env.keys()):
                if any(m in k.lower() for m in keyword_mask):
                    env[k] = "*" * len(k)  # masque simple

        return env


if __name__ == "__main__":
    tmdb = TmdbService()
    film = tmdb.get_movie_filtered("Titanic", 5)

    print("\n=== FILM TMDB (FILTRÉ) ===")
    print("ID          :", film["id_film"])
    print("Titre       :", film["titre"])
    print("Réalisateur :", film["realisateur"])
    print("Genres      :", ", ".join(film["genres"]))
    print("Casting     :", ", ".join(film["casting"]))
    print("==========================\n")
