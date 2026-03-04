import logging

from src.business_object.user import User
from src.service.tmdb_service import TmdbService
from src.service.user_service import UserService
from src.utils.log_decorator import log


class UserClient:
    def __init__(self):
        self.user_service = UserService()
        self.tmdb_service = TmdbService()

    def signup(self, pseudo, email, password):
        try:
            user = User(pseudo=pseudo, email=email, psswd=password)
            self.user_service.signup(user)
            return {"status": "ok", "pseudo": pseudo}
        except ValueError as v:
            logging.error(f"Pseudo ou mot de passe non conforme : {v}")

    def login(self, pseudo, password):
        return self.user_service.login(pseudo, password)

    @log
    def add_favorite(self, pseudo, password, titre):
        try:
            user = self.login(pseudo, password)
            if not user:
                logging.error("Pseudo ou mot de passe incorrect")
                return {"status" : "error"}

            film = self.tmdb_service.get_movie_filtered(titre)
            self.user_service.add_favorite(pseudo, film)

            return {
                "status" : "ok",
                "titre" : film.titre,
                "realisateur" : film.realisateur,
                "annee" : film.annee
            }
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de favori : {e}")

    def get_favorites(self, pseudo, password):
        try:
            user = self.login(pseudo, password)
            if not user:
                logging.error("Pseudo ou mot de passe incorrect")
                return {"status" : "error"}

            favorites = self.user_service.get_favorites(pseudo)

            dico = {
                "status" : "ok",
                "films" : []
            }

            for film in favorites:
                dico["films"].append({
                    "titre" : film.titre,
                    "realisateur" : film.realisateur
                })

            return dico

        except Exception as e:
            logging.error(f"Erreur lors de la récupération des favoris : {e}")
