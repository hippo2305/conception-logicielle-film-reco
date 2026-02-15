import re

import pytest

from src.business_object import User


@pytest.mark.parametrize(
    "params, error_type, error_message",
    [
        # test d'erreur sur le pseudo du user
        (
            {
                "pseudo": 1252,
                "email": "dolel@ejemme.com",
                "psswd": "dleoele545485Qp@",
                "listfilms": ["MadMax"],
            },
            TypeError,
            "Le pseudo doit être une chaîne de caractères.",
        ),
        (
            {
                "pseudo": "",
                "email": "dolel@ejemme.com",
                "psswd": "dleoele545485Qp@",
                "listfilms": ["MadMax"],
            },
            ValueError,
            "Le pseudo ne peut pas être vide.",
        ),
        # test d'erreur sur le mail du user.
        # Juste erreur de type, le reste est fait dans user_service
        (
            {
                "pseudo": "groupe-20",
                "email": 45222,
                "psswd": "dleoele545485Qp@",
                "listfilms": ["MadMax"],
            },
            TypeError,
            "L'email doit être une chaîne de caractères.",
        ),
        (
            {
                "pseudo": "groupe-20",
                "email": "",
                "psswd": "dleoele545485Qp@",
                "listfilms": ["MadMax"],
            },
            ValueError,
            "L'adresse mail ne peut pas être vide.",
        ),
        # test d'erreur sur le password du user
        (
            {
                "pseudo": "groupe-20",
                "email": "djamal.toe@gmail.com",
                "psswd": 150,
                "listfilms": ["MadMax"],
            },
            TypeError,
            "Le mot de passe doit être une chaîne de caractères.",
        ),
        (
            {
                "pseudo": "groupe-20",
                "email": "djamal.toe@gmail.com",
                "psswd": "",
                "listfilms": ["MadMax"],
            },
            ValueError,
            "Mot de passe invalide",
        ),
        (
            {
                "pseudo": "groupe-20",
                "email": "djamal.toe@gmail.com",
                "psswd": "150",
                "listfilms": "MadMax",
            },
            TypeError,
            "Le paramètre listfilms doit être une liste.",
        ),
    ],
)

# fonction pour tester les erreurs en fonction de
# la paramétrisation ci-dessus
def test_user_init_echec(params, error_type, error_message):
    with pytest.raises(error_type, match=re.escape(error_message)):
        User(**params)
