import os

import pytest

from src.utils.psswd_proc import PasswordProcessing


# -----------------------------
# Fixture : mot de passe valide
# -----------------------------
@pytest.fixture
def valid_password():
    """Retourne un mot de passe valide pour les tests."""
    return "Password1@"


# -----------------------------
# Fixture : instance PasswordProcessing
# -----------------------------
@pytest.fixture
def password_processor(valid_password):
    """Crée une instance PasswordProcessing avec un mot de passe donné."""
    return PasswordProcessing(valid_password)


# -----------------------------
# Test de la méthode validate_password (paramétrisé)
# -----------------------------
@pytest.mark.parametrize(
    "pwd, expected",
    [
        ("Password1@", True),  # valide
        ("pass", False),  # trop court
        ("password1@", False),  # pas de majuscule
        ("PASSWORD@", False),  # pas de chiffre
        ("Password1", False),  # pas de caractère spécial
        ("Pass1@", False),  # trop court et valide pour le reste
    ],
)
def test_validate_password(pwd, expected):
    """
    Teste la méthode statique validate_password pour différents mots de passe.
    Vérifie si les règles de sécurité sont respectées :
    - longueur minimale
    - majuscule
    - chiffre
    - caractère spécial
    """
    # On définit la longueur minimale via la variable d'environnement pour tester correctement
    os.environ["PASSWORD_LENGTH"] = "8"
    assert PasswordProcessing.validate_password(pwd) is expected


# -----------------------------
# Test du hash et de la vérification
# -----------------------------
def test_hash_and_verify(password_processor, valid_password):
    """
    Teste que :
    - le hash est bien généré
    - un mot de passe correct est validé
    - un mot de passe incorrect est rejeté
    """
    # Génère un hash
    hashed = password_processor._hash_password()

    # Vérifie que c'est un bytes
    assert isinstance(hashed, bytes)

    # Vérifie le mot de passe correct
    assert password_processor._verify_password(valid_password, hashed) is True

    # Vérifie qu'un mot de passe incorrect retourne False
    assert password_processor._verify_password("WrongPass1@", hashed) is False


# -----------------------------
# Test de l'encodage en bytes
# -----------------------------
def test_password_is_bytes(password_processor):
    """
    Vérifie que l'attribut password est bien encodé en bytes pour bcrypt.
    """
    assert isinstance(password_processor.password, bytes)
