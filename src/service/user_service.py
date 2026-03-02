import logging
import os
import re

from src.business_object.admin import Admin
from src.business_object.client import Client
from src.business_object.film import Film
from src.business_object.user import User
from src.dao.user_dao import UserDao
from src.service.session_manager import SessionManager
from src.utils.log_decorator import log
from src.utils.psswd_proc import PasswordProcessing


class UserService:
    """
    Service métier pour gérer les utilisateurs et les données liées aux stations.
    Utilise la session pour identifier l'utilisateur courant sans avoir à passer son pseudo.
    """

    def __init__(
        self,
        user_dao: UserDao = None,
    ):
        self.user_dao: UserDao = user_dao if user_dao else UserDao()
        self.session_manager: SessionManager = SessionManager()
        self.current_session = None

    @staticmethod
    def validate_email(email: str):
        """
        Permet de valider l'email entrée par un utilisateur.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email)

    def signup(self, user: User, role: str = "client") -> User:
        """
        Cette méthode peut être utilliser par un nouvel utilisateur
        souhaitant créer un compte ou par l'administrateur dans le but
        de créer un compte pour une tierse personne.
        """
        if not isinstance(user, User):
            raise TypeError("L'utilisateur doit être de type User")

        if not self.validate_email(user.email):
            raise Exception("L'email n'est pas valide")

        verif_user_existed = self.user_dao.get_by_pseudo(user.pseudo)
        if verif_user_existed:
            message = f"Le pseudo '{user.pseudo}' est déjà utilisé."
            raise Exception(message)

        all_users = self.user_dao.get_all_users()
        # for user_ in all_users:
        if any(user_.email == user.email for user_ in all_users):
            message = f"Le mail '{user.email}' est déjà utilisé."
            raise Exception(message)

        password_processor = PasswordProcessing(user._psswd)
        if not password_processor.validate_password(user._psswd):
            message = (
                "Le mot de passe entré est invalide.\n"
                "Il doit contenir une majuscule, un caractère spécial, \n"
                "et faire au moins 8 caractères."
            )
            raise Exception(message)

        #  on change le password du user en le remplaçant par celui hashé
        user._psswd = password_processor._hash_password().decode("utf-8")

        #  on essaie de créer l'utilisateur avec la méthode create du DAO
        user_created = self.user_dao.create(user=user, role=role)
        if user_created:
            return user
        else:
            message = "Échec de la création de l'utilisateur."
            raise Exception(message)

    def login(self, pseudo: str, psswd: str) -> Client | Admin:
        """
        Connecte un utilisateur et crée sa session.
        Stocke la session dans self.current_session.
        """
        user = self.user_dao.get_by_pseudo(pseudo)
        if not user:
            message = "Utilisateur non trouvé."
            raise Exception(message)

        if not PasswordProcessing._verify_password(
            None, psswd, user._psswd.encode("utf-8")
        ):
            message = "Mot de passe incorrect."
            raise Exception(message)

        self.current_session = self.session_manager.create_session(user)

        return user

    def logout(self) -> bool:
        """
        Déconnecte l'utilisateur courant et termine sa session.
        L'action réalisée est loguée dans la base de données.
        """
        pseudo = self.current_session.user.pseudo

        # On ferme la session courante
        self.session_manager.logout(pseudo)
        self.current_session = None

    def change_user_role(self, pseudo: str, new_role: str = "") -> bool:
        """
        Permet de changer le rôle d'un utilisateur de client vers admin mais
        jamais dans l'autre sens. Seuls les administrateurs ont le droit.
        """
        actor = self.current_session.user

        if actor.role != "admin":
            message = "Seuls les administrateurs peuvent modifier les rôles."
            raise Exception(message)

        concerned_user = self.user_dao.get_by_pseudo(pseudo)
        if not concerned_user:
            message = "L'utilisateur dont vous tentez de changer le rôle n'existe pas"
            raise Exception(message)

        if concerned_user.role == "admin":
            message = "Vous ne pouvez pas modifier le rôle d'un Administrateur"
            raise Exception(message)

        changed = self.user_dao.change_user_role(pseudo=pseudo, new_role=new_role)
        return changed

    def change_user_email(self, pseudo: str, new_email: str) -> bool:
        if not isinstance(pseudo, str):
            raise TypeError("Le pseudo doit être une chaîne de caractères")

        if not isinstance(new_email, str):
            raise TypeError("L'email doit être une chaîne de caractères")

        if not self.validate_email(email=new_email):
            raise Exception("Adresse email invalide.")

        actor = self.current_session.user

        # Si l'utilisateur modifie son propre mail
        if actor.pseudo == pseudo:
            try:
                email_changed = self.user_dao.change_user_email(
                    pseudo=actor.pseudo, new_email=new_email
                )
                return email_changed
            except Exception as e:
                raise Exception(
                    f"Une erreur innatendue s'est produite\n {e}"
                ) from e

        # Si l'utilisateur est admin, il peut modifier celui d’un client
        if actor.role == "admin":
            concerned_user = self.user_dao.get_by_pseudo(pseudo=pseudo)
            if not concerned_user:
                raise Exception(
                    "L'utilisateur dont vous tentez de modifier le courriel n'existe pas"
                )
            if concerned_user.role != "client":
                raise Exception(
                    "Vous ne pouvez modifier que le courriel d’un client"
                )

            try:
                email_changed = self.user_dao.change_user_email(
                    pseudo=pseudo, new_email=new_email
                )
                return email_changed
            except Exception as e:
                raise Exception(
                    f"Une erreur innatendue s'est produite\n {e}"
                ) from e

        # Si c’est un client qui veut modifier un autre utilisateur
        raise Exception(
            "Vous ne disposez pas des accès nécessaires pour"
            "modifier le courriel d’un autre utilisateur"
        )

    def change_user_mdp(self, pseudo: str, new_psswd: str) -> bool:
        """
        Permet de changer le mot de passe d'un utilisateur.
        Si l'utilisateur est un client, il ne peut changer que son propre mot de passe.
        Les administrateurs peuvent changer le mot de passe de n'importe quel client.
        """
        if not isinstance(pseudo, str):
            raise TypeError("Le pseudo doit être une chaîne de caractères")
        if not isinstance(new_psswd, str):
            raise TypeError("Le mot de passe doit être une chaîne de caractères")

        password_processor = PasswordProcessing(new_psswd)
        if not PasswordProcessing.validate_password(new_psswd):
            message = (
                "Mot de passe invalide ! Il doit contenir majuscule, chiffre et caractère spécial"
                f" et faire {os.environ['PASSWORD_LENGTH']}."
            )
            raise Exception(message)

        actor = self.current_session.user
        new_psswd = password_processor._hash_password().decode("utf-8")
        if actor.pseudo == pseudo:
            changed = self.user_dao.change_mdp(pseudo=pseudo, new_psswd=new_psswd)
            return changed

        if actor.role != "admin":
            raise Exception(
                "Vous ne pouvez pas changer le mot de passe d'un autre utilisateur"
            )

        concerned_user = self.user_dao.get_by_pseudo(pseudo)
        if not concerned_user:
            raise Exception("Cet utilisateur n'existe pas.")

        if concerned_user.role == "admin":
            raise Exception(
                "Vous ne pouvez pas modifier le mot de passe d'un autre administrateur"
            )

        changed = self.user_dao.change_mdp(pseudo=pseudo, new_psswd=new_psswd)

        return changed

    def delete_user(self, pseudo: str) -> bool:
        """
        Un admin supprime un compte.

        """
        if not isinstance(pseudo, str):
            raise TypeError("Le pseudo doit être une chaîne de caractères")

        actor = self.current_session.user
        target_user = self.user_dao.get_by_pseudo(pseudo)
        if not target_user:
            raise Exception(f"L'utilisateur '{pseudo}' n'existe pas.")

        elif actor.role == "admin" and target_user.role != "admin":
            success = self.user_dao.delete_user(pseudo)
        else:
            raise Exception(
                "Vous n'avez pas les droits pour supprimer ce compte."
            )

        return success

    def search_user(self, pseudo: str):
        """
        Permet de rechercher un utilisateur à partir de son pseudonyme.
        Réservée aux administrateurs (sauf auto-consultation).
        """
        if not isinstance(pseudo, str):
            raise TypeError("Le pseudo doit être une chaine de caractères")

        actor = self.current_session.user
        if actor.role != "admin" and actor.pseudo != pseudo:
            raise Exception(
                "Vous n'avez pas les droits requis pour effectuer cette recherche."
            )

        searched_user = self.user_dao.get_by_pseudo(pseudo=pseudo)

        return searched_user

    def get_all_users(self):
        """
        Retourne tous les utilisateurs de la base de données.
        Réservée aux administrateurs.
        """

        actor = self.current_session.user
        if actor.role != "admin":
            raise Exception(
                "Vous n'avez pas les droits requis pour effectuer cette recherche."
            )

        users_list = self.user_dao.get_all_users()

        return users_list

    @log
    def add_favorite(self, pseudo: str, film: Film):
        try:
            user = self.user_dao.get_by_pseudo(pseudo)
            favorites = self.user_dao.get_favorites(user)
            if favorites:
                favorites.append(film)
            else:
                favorites = [film]
            user.listfilms = favorites
            self.user_dao.add_favorites(user)
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout des favoris : {e}")
            return False

    def get_favorites(self, pseudo: str):
        try:
            user = self.user_dao.get_by_pseudo(pseudo)
            return self.user_dao.get_favorites(user)
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des favoris : {e}")
            return None
