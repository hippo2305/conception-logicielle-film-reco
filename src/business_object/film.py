class Film:
    """
    Cette classe représente un film.

    Attributs
    ----------
    titre : str
        Titre du film
    realisateur : str
        Réalisateur du film
    genre : str
        Genre du film
    casting : list[Actor]
        Liste des acteurs du film
    """

    def __init__(self, titre: str, realisateur: str, genre: str, casting: list):
        """Constructeur"""
        self.titre = titre
        self.realisateur = realisateur
        self.genre = genre
        self.casting = casting

    def __str__(self):
        """Affichage lisible d'un film"""
        return (
            f"Film(titre='{self.titre}', "
            f"réalisateur='{self.realisateur}', "
            f"genre='{self.genre}', "
            f"casting={len(self.casting)} acteurs)"
        )

    def description(self):
        """Description textuelle du film"""
        return f"'{self.titre}', un film de {self.realisateur} (genre : {self.genre})"
