class User:
    """
    Représente un utilisateur générique du système.

    Attributes
    ----------
    pseudo : str
        Le pseudo unique de l'utilisateur.
    email : str
        L'adresse email de l'utilisateur.
    psswd : str
        Le mot de passe de l'utilisateur (hashé dans la couche service).
    listfilms : list[film]
        La liste des films déjà vus
    """

    def __init__(
        self,
        pseudo: str,
        email: str,
        psswd: str,
        listfilms: list,
    ):
        if not isinstance(pseudo, str):
            raise TypeError("Le pseudo doit être une chaîne de caractères.")
        if not isinstance(email, str):
            raise TypeError("L'email doit être une chaîne de caractères.")
        if not isinstance(psswd, str):
            raise TypeError("Le mot de passe doit être une chaîne de caractères.")
        if not isinstance(listfilms, list):
            raise TypeError("Le paramètre listfilms doit être une liste.")

        if not pseudo.strip():
            raise ValueError("Le pseudo ne peut pas être vide.")

        if not email.strip():
            raise ValueError("L'adresse mail ne peut pas être vide.")

        if not psswd.strip():
            raise ValueError("Mot de passe invalide.")

        self.pseudo = pseudo.strip()
        self.email = email.strip().lower()
        self._psswd = psswd
        self.listfilms = listfilms

    def __str__(self) -> str:
        """
        Retourne une représentation lisible de l'utilisateur.

        Returns
        -------
        str
            Chaîne contenant le pseudo et l'email.
        """
        return f"User(pseudo='{self.pseudo}', email='{self.email}')"
