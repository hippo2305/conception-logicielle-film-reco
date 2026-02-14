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

    def __init__(self, titre: str, realisateur: str, genre: str, casting=None):
        """Constructeur"""
        self.titre = titre
        self.realisateur = realisateur
        self.genre = genre
        self.casting = casting

    def __str__(self):
        """Affichage lisible d'un film"""
        string = (
            f"Film(titre='{self.titre}', "
            f"réalisateur='{self.realisateur}', "
            f"genre='{self.genre}'"
        )
        if self.casting:
            string += f", casting={len(self.casting)} acteurs"

        return string + ")"

    def description(self):
        """Description textuelle du film"""
        return f"'{self.titre}', un film de {self.realisateur} (genre : {self.genre})"
