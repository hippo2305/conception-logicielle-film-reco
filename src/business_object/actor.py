class Actor:
    """
    Cette classe représente un acteur.

    Attributs
    ----------
    nom : str
        Nom de l'acteur
    prenom : str
        Prénom de l'acteur
    """

    def __init__(self, nom: str, prenom: str):
        """Constructeur"""
        self.nom = nom
        self.prenom = prenom

    def __str__(self):
        """Affichage lisible d'un acteur"""
        return f"Actor(nom='{self.nom}', prenom='{self.prenom}')"

    def description(self):
        """Description textuelle de l'acteur"""
        return f"{self.prenom} {self.nom}"
