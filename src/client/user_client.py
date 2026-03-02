import logging

from src.business_object.user import User
from src.client.film_client import FilmClient
from src.service.user_service import UserService
from src.utils.log_decorator import log


class UserClient:
    def __init__(self):
        self.user_service = UserService()
        self.film_client = FilmClient()

    def signup(self, pseudo, email, password):
        try:
            user = User(pseudo=pseudo, email=email, psswd=password)
            self.user_service.signup(user)
            return {"status": "ok", "pseudo": pseudo}
        except ValueError as v:
            logging.error(f"Pseudo ou mot de passe non conforme : {v}")

    def login(self, pseudo, password):
        return self.user_service.login(pseudo, password)

    def authenticate_user(self, pseudo: str, password: str):
        try:
            return self.login(pseudo, password)
        except ValueError as v:
            logging.error(f"Erreur lors de l'authentification : {v}")
            return None

    @log
    def add_favorite(self, pseudo, password, titre):
        try:
            user = self.authenticate_user(pseudo, password)
            if not user:
                logging.error("Pseudo ou mot de passe incorrect")
                return {"status" : "error"}

            film = self.film_client.get_film_tmdb(titre)
            self.user_service.add_favorite(user.pseudo, film)

            return {
                "status" : "ok",
                "titre" : film.titre,
                "realisateur" : film.realisateur
            }
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de favori : {e}")

    def get_favorites(self, pseudo, password):
        try:
            user = self.authenticate_user(pseudo, password)
            if not user:
                logging.error("Pseudo ou mot de passe incorrect")
                return {"status" : "error"}

            favorites = self.user_service.get_favorites(pseudo)

            dict = {
                "status" : "ok",
                "films" : []
            }

            for film in favorites:
                dict["films"].append({
                    "titre" : film.titre,
                    "realisateur" : film.realisateur
                })
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des favoris : {e}")
