from business_object.user import User


class Admin(User):
    """
    Classe représentant un administrateur du système, héritée de `User`.

    Un administrateur dispose de privilèges étendus sur les autres utilisateurs.

    Attributes
    ----------
    pseudo : str
        Le pseudo de l'administrateur.
    email : str
        L'adresse email de l'administrateur.
    _psswd : str
        Le mot de passe de l'administrateur.
    listfilms : list[films]
        La liste des films déjà vus
    _role : str
        Le rôle associé, par défaut "admin".
    """

    def __init__(
        self,
        pseudo: str,
        email: str,
        psswd: str,
        listfilms: list,
        role: str = "admin",
    ):
        super().__init__(pseudo, email, psswd, listfilms)
        self._role = role

    @property
    def role(self) -> str:
        """Retourne le rôle de l'administrateur."""
        return self._role

    def __str__(self) -> str:
        """
        Retourne une représentation lisible de l'administrateur.

        Returns
        -------
        str
            Chaîne contenant pseudo, email, rôle et date de création.
        """
        return (
            f"Admin(pseudo='{self.pseudo}', email='{self.email}', role='{self._role}')"
        )
