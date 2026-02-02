import os

from dotenv import load_dotenv


class MAIN:
    def load_env():
        # Charge le fichier principal
        load_dotenv()
        # Charge un fichier local si présent
        local_env_path = ".env.local"
        if os.path.exists(local_env_path):
            load_dotenv(dotenv_path=local_env_path, override=True)

    def get_local_env():
        local_env_path = ".env.local"

        if os.path.exists(local_env_path):
            load_dotenv(dotenv_path=local_env_path)

        keyword_mask = [
            "password",
            "pwd",
            "jeton",
            "token",
            "secret",
            "key",
            "cle",
            "mdp",
            "motdepasse",
        ]

        for key, value in os.environ.items():
            if any(mask in key.lower() for mask in keyword_mask):
                print(f"{key}=", end="")
                for _i in range(len(key)):
                    print("*", end="")
                print("")
            else:
                print(f"{key}={value}")


if __name__ == "__main__":
    print(MAIN.get_local_env())
