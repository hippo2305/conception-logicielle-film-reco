import logging

from src.business_object.admin import Admin
from src.business_object.client import Client
from src.business_object.film import Film
from src.business_object.user import User
from src.dao.dao import DAO
from src.dao.film_dao import FilmDAO
from src.utils.log_decorator import log


class UserDao:
    """
    Classe d'accès aux données pour la table 'users'.

    Cette classe implémente le pattern DAO (Data Access Object) pour gérer
    toutes les opérations CRUD (Create, Read, Update, Delete) sur les
    utilisateurs.

    Attributs
    ---------
    db_conn : connexion
        Connexion active à la base de données PostgreSQL/MySQL
    """

    def __init__(self):
        """
        Initialise le DAO des utilisateurs.

        """
        self.dao = DAO()
        self.film_dao = FilmDAO()

    @log
    def create(self, user: User, role: str = "client") -> bool:
        """
        Insère un nouvel utilisateur dans la table 'users'.
        """
        try:
            self.dao.insert_query(
                "USERS", "pseudo, email, mdp, user_role",
                f"{user.pseudo}, {user.email}, {user.psswd}, {role}"
            )
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'insertion de l'utilisateur : {e}")
            return False

    @log
    def add_favorites(self, user: User) -> bool:
        """
        Ajoute le casting d'un film dans la BDD et ajoute les associations
        """
        try:
            id_user = self.get_id(user)

            # Ajout des acteurs si non présents dans la BDD et récupération des id
            if user.listfilms:
                for film in user.listfilms:
                    # N'ajoute l'acteur que s'il n'est pas déjà dans la BDD
                    if not self.film_dao.exists(film):
                        self.film_dao.add_film(film)
                    id_film = self.film_dao.get_id(film)

                    # vérification que l'association n'existe pas déjà
                    if self.dao.select_query(
                        "FAVORIS",
                        "1",
                        where=f"id_user = '{id_user}' AND id_film = '{id_film}'",
                    ) is None:

                        # Insertion dans la table d'association
                        self.dao.insert_query(
                            "FAVORIS", "id_user, id_film", f"{id_user}, {id_film}"
                        )

                return True

            else:
                logging.info(f"Les favoris de l'utilisateur {user.pseudo} ne sont pas renseignés.")

        except Exception as e:
            logging.error(f"Erreur lors de l'ajout des favoris' : {e}")
            return None

    @log
    def login(self, pseudo: str):
        """
        Récupère un utilisateur par son pseudo pour une tentative de connexion.

        Recherche l'utilisateur dans la base et retourne un objet Admin ou
        Client selon son rôle. Cette méthode NE vérifie PAS le mot de passe,
        elle se contente de récupérer les données.

        Parameters
        ----------
        pseudo : str
            Le pseudo de l'utilisateur qui tente de se connecter
        psswd : str
            Le mot de passe fourni (non utilisé dans cette méthode,
            la vérification se fait dans le Service)

        Sécurité
        --------
        Le mot de passe retourné est le hash stocké en base, jamais le mot
        de passe en clair. La comparaison avec le mot de passe fourni doit
        se faire dans le Service avec une fonction de vérification de hash.

        """
        try:
            res = self.dao.select_query("USERS", where = f"pseudo = {pseudo}")

            if res[4] == "client":
                return Client(
                    pseudo=res[1],
                    email=res[2],
                    psswd=res[3],
                    role=res[4],
                )
            else:
                return Admin(
                    pseudo=res[1],
                    email=res[2],
                    psswd=res[3],
                    role=res[4],
                )
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'utilisateur : {e}")
            return None

    @log
    def change_user_email(self, pseudo: str, new_email: str) -> bool:
        """
        Modifie l'email associé au compte utilisateur. Cette opération peut
        nécessiter une vérification par email dans un cas réel.

        """
        try:
            self.dao.update_query("USERS", "email", f"{new_email}", f"pseudo = {pseudo}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors du changement d'email : {e}")
            return False

    @log
    def change_mdp(self, pseudo: str, new_psswd: str) -> bool:
        """
        Enregistre un nouveau hash de mot de passe pour l'utilisateur.
        Le mot de passe fourni DOIT déjà être hashé.

        """
        try:
            self.dao.update_query("USERS", "mdp", f"{new_psswd}", f"pseudo = {pseudo}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors du changement de mot de passe : {e}")
            return False

    @log
    def delete_user(self, pseudo: str) -> bool:
        """
        Supprime définitivement un utilisateur de la base de données.
        """
        try:
            self.dao.del_query("USERS", f"pseudo = {pseudo}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la suppression de l'utilisateur : {e}")
            return False

    @log
    def get_id(self, user: User) -> int:
        """
        Récupère l'id d'un utilisateur dans la BDD
        """
        try:
            # Récupération de l'id
            res = self.dao.select_query(
                "USERS",
                "id_user",
                where=f"pseudo = '{user.pseudo}'",
            )
            return res[0]

        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'id : {e}")
            return None

    @log
    def get_favorites(self, user : User):
        """
        Récupère tous les films favoris d'un utilisateur
        """
        try:
            # Récupère l'id du l'utilisateur
            id_user = self.get_id(user)

            rows = self.dao.select_query(
                "FILM f",
                "f.id_film, f.titre, f.realisateur, f.annee, f.genre",
                "FAVORIS fav ON fav.id_film = f.id_film",
                f"fav.id_user = {id_user}",
                "ORDER BY f.titre ASC",
                multiple=True,
            )

        except Exception as e:
            logging.error(f"Erreur lors de la récupération des films : {e}")
            return None

        return [Film(row[1], row[2], row[3], row[4]) for row in rows] if rows else None

    @log
    def get_all_users(self) -> list[User]:
        """
        Récupère tous les utilisateurs de la base de données.
        """
        try:
            res = self.dao.select_query("USERS", multiple = True)
            if res is None:
                return None
            users = []
            for row in res:
                user = User(
                    pseudo=row[1],
                    email=row[2],
                    psswd=row[3],
                )
                users.append(user)
            return users
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des utilisateurs : {e}")
            return None

    @log
    def get_by_id(self, id: int) -> User | None:
        """
        Récupère un utilisateur spécifique par son identifiant.
        """
        try:
            res = self.dao.select_query("USERS", where = f"id_user = {id}")
            if not res:
                return None

            if res[4] == "client":
                return Client(
                    pseudo=res[1],
                    email=res[2],
                    psswd=res[3],
                )
            else:
                return Admin(
                    pseudo=res[1],
                    email=res[2],
                    psswd=res[3],
                )
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'utilisateur : {e}")
            return None

    @log
    def get_by_pseudo(self, pseudo: str) -> User | None:
        """
        Récupère un utilisateur spécifique par son pseudo.
        """
        try:
            res = self.dao.select_query("USERS", where = f"pseudo = {pseudo}")
            if not res:
                return None

            if res[4] == "client":
                return Client(
                    pseudo=res[1],
                    email=res[2],
                    psswd=res[3],
                )
            else:
                return Admin(
                    pseudo=res[1],
                    email=res[2],
                    psswd=res[3],
                )
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'utilisateur : {e}")
            return None
