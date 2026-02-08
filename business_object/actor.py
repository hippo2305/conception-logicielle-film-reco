class Actor:
    """
    Cette classe représente un acteur.

    Attributs
    ----------
    nom : str
        Nom de l'acteur
    prenom : str
        Prénom de l'acteur
    age : int
        Âge de l'acteur
    films : list[Film]
        Liste des films dans lesquels l'acteur a joué
    """

    def __init__(self, nom: str, prenom: str):
        """Constructeur"""
        self.nom = nom
        self.prenom = prenom

    def __str__(self):
        """Affichage lisible d'un acteur"""
        return (
            f"Actor(nom='{self.nom}', "
            f"prenom='{self.prenom}', "
        )

    def description(self):
        """Description textuelle de l'acteur"""
        return (
            f"{self.prenom} {self.nom}"
        )
