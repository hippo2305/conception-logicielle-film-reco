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

    def __init__(self, nom: str, prenom: str, age: int, films: list):
        """Constructeur"""
        self.nom = nom
        self.prenom = prenom
        self.age = age
        self.films = films

    def __str__(self):
        """Affichage lisible d'un acteur"""
        return (
            f"Actor(nom='{self.nom}', "
            f"prenom='{self.prenom}', "
            f"age={self.age}, "
            f"films={len(self.films)} films)"
        )

    def description(self):
        """Description textuelle de l'acteur"""
        return (
            f"{self.prenom} {self.nom}, {self.age} ans, "
            f"a joué dans {len(self.films)} film(s)"
        )
