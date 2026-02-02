import os
import re

import bcrypt
import dotenv


class PasswordProcessing:
    """
    Classe utilitaire pour gérer le hachage, la vérification et la validation
    de mots de passe de manière sécurisée avec bcrypt.
    """

    def __init__(self, password: str):
        """
        Initialise le gestionnaire avec un mot de passe.
        """
        dotenv.load_dotenv()
        self.password = password.encode("utf-8")  # bcrypt attend des bytes

    def _hash_password(self) -> bytes:
        """
        Génère un hash bcrypt du mot de passe avec un sel aléatoire.
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(self.password, salt=salt)

    def _verify_password(self, entered_password: str, hashed_password: bytes) -> bool:
        """
        Vérifie si un mot de passe entré correspond à un mot de passe hashé.
        """
        return bcrypt.checkpw(
            password=entered_password.encode("utf-8"),
            hashed_password=hashed_password,
        )

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Vérifie que le mot de passe respecte les règles de sécurité :
        - Minimum x caractères (x dans .env)
        - Contient au moins une majuscule
        - Contient au moins un chiffre
        - Contient au moins un caractère spécial (@, #, $, !, %, ^, &, *)

        """
        if len(password) < int(os.environ["PASSWORD_LENGTH"]):
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[@#$!%^&*]", password):
            return True
