from ast import List

from business_object import Admin, Client, User
from dao import connexion
from utils import Logger


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
    logger : Logger
        Instance du logger pour enregistrer les erreurs
    """

    def __init__(self):
        """
        Initialise le DAO des utilisateurs.

        Établit la connexion à la base de données et initialise le logger.
        Cette méthode est appelée automatiquement lors de la création d'une
        instance de UserDao.

        Raises
        ------
        Exception
            Si la connexion à la base de données échoue
        """
        self.db_conn = connexion().connection
        self.logger = Logger()

    def create(self, user: User, role: str = "client") -> bool:
        """
        Insère un nouvel utilisateur dans la table 'users'.
        """
        sql = (
            "INSERT INTO users (pseudo, email, listfilms, password, role, "
            "creation_date) VALUES (%s, %s, %s, %s, %s);"
        )

        values = (
            user.pseudo,
            user.email,
            user.psswd,
            user.listfilms,
            role,
        )

        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(sql, values)
            self.db_conn.commit()
            return True
        except Exception as e:
            self.db_conn.rollback()
            self.logger.error(f"Erreur lors de l'insertion : {e}")
            return False

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
        sql = "SELECT * FROM users WHERE pseudo = %s;"
        values = (pseudo,)

        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(sql, values)
                res = cursor.fetchone()

                if res:
                    if res["role"] == "client":
                        return Client(
                            pseudo=res["pseudo"],
                            email=res["email"],
                            psswd=res["password"],
                            listfilms=res["listfilms"],
                            role=res["role"],
                        )
                    else:
                        return Admin(
                            pseudo=res["pseudo"],
                            email=res["email"],
                            psswd=res["password"],
                            listfilms=res["listfilms"],
                            role=res["role"],
                        )
            return None
        except Exception as e:
            self.db_conn.rollback()
            self.logger.error(f"Erreur lors du login : {e}")
            return None

    def change_user_email(self, pseudo: str, new_email: str) -> bool:
        """
        Modifie l'email associé au compte utilisateur. Cette opération peut
        nécessiter une vérification par email dans un cas réel.

        """
        sql = "UPDATE users SET email = %s WHERE pseudo = %s;"
        values = (new_email, pseudo)
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(sql, values)
                self.db_conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Erreur lors du changement d'email : {e}")
            self.db_conn.rollback()
            return False

    def change_mdp(self, pseudo: str, new_psswd: str) -> bool:
        """ ""
        Enregistre un nouveau hash de mot de passe pour l'utilisateur.
        Le mot de passe fourni DOIT déjà être hashé.

        """
        sql = "UPDATE users SET password = %s WHERE pseudo = %s;"
        values = (new_psswd, pseudo)
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(sql, values)
                self.db_conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Erreur lors du changement du mot de passe : {e}")
            self.db_conn.rollback()
            return False

    def delete_user(self, pseudo: str) -> bool:
        """
        Supprime définitivement un utilisateur de la base de données.
        """
        sql = "DELETE FROM users WHERE pseudo = %s;"
        values = (pseudo,)

        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(sql, values)
                self.db_conn.commit()
                return cursor.rowcount > 0
        except Exception:
            self.db_conn.rollback()
            return False

    def get_all_users(self) -> List[User] | None:
        """
        Récupère tous les utilisateurs de la base de données.
        """
        sql = "SELECT * FROM users;"
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
                if not res:
                    return None

                users = []
                for row in res:
                    if row["role"] == "admin":
                        user = Admin(
                            pseudo=res["pseudo"],
                            email=res["email"],
                            psswd=res["password"],
                            listfilms=res["listfilms"],
                            role=res["role"],
                        )
                    else:
                        user = Client(
                            pseudo=res["pseudo"],
                            email=res["email"],
                            psswd=res["password"],
                            listfilms=res["listfilms"],
                            role=res["role"],
                        )
                    users.append(user)
                return users

        except Exception as e:
            self.db_conn.rollback()
            self.logger.error(f"Erreur lors de la récupération des utilisateurs : {e}")
            return None

    def get_user_by_pseudo(self, pseudo: str) -> User | None:
        """
        Récupère un utilisateur spécifique par son pseudo.
        """
        sql = "SELECT * FROM users WHERE pseudo = %s;"
        values = (pseudo,)

        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(sql, values)
                res = cursor.fetchone()
                if not res:
                    return None

                if res["role"] == "client":
                    return Client(
                        pseudo=res["pseudo"],
                        email=res["email"],
                        psswd=res["password"],
                        listfilms=res["listfilms"],
                        role=res["role"],
                    )
                else:
                    return Admin(
                        pseudo=res["pseudo"],
                        email=res["email"],
                        psswd=res["password"],
                        listfilms=res["listfilms"],
                        role=res["role"],
                    )

        except Exception as e:
            self.db_conn.rollback()
            self.logger.error(f"Erreur lors de la récupération de l'utilisateur : {e}")
            return None
