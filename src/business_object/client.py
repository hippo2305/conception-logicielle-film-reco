from src.business_object.user import User


class Client(User):
    """
    Classe représentant un client du système, héritée de `User`.

    Cette classe ajoute un attribut de rôle spécifique ("client")
    et conserve les attributs et validations de la classe parente.

    Attributes
    ----------
    pseudo : str
        Le pseudo unique du client (hérité de User).
    email : str
        L'adresse email du client (hérité de User).
    _psswd : str
        Le mot de passe du client (hashé dans la couche Service).
    listfilms : list[film]
        La liste des films déjà vus
    _role : str
        Le rôle du client, par défaut "client".

    """

    def __init__(
        self,
        pseudo: str,
        email: str,
        psswd: str,
        listfilms: list,
        role: str = "client",
    ):
        super().__init__(pseudo, email, psswd, listfilms)
        self._role = role

    @property
    def role(self) -> str:
        """
        Retourne le rôle actuel du client.

        """
        return self._role

    @role.setter
    def role(self, value: str):
        """
        Modifie le rôle du client.

        Parameters
        ----------
        value : str
            Nouveau rôle à attribuer au client.
        """
        if not isinstance(value, str):
            raise TypeError("Le rôle doit être une chaîne de caractères.")
        self._role = value

    def __str__(self) -> str:
        """
        Retourne une représentation lisible et concise du client.

        Returns
        -------
        str
            Une chaîne descriptive du client, sans mot de passe.
        """
        return (
            f"Client(pseudo='{self.pseudo}', email='{self.email}', role='{self._role}')"
        )
