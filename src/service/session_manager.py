from src.business_object.user import User
from src.service.session import Session


class SessionManager:
    """
    Gère toutes les sessions utilisateurs en mémoire.
    Permet de récupérer la session active courante pour simplifier l'utilisation
    dans UserService.
    """

    def __init__(self):
        self.sessions = {}  # clé = pseudo, valeur = Session
        self.current_session: Session | None = None  # session active courante

    def create_session(self, user: User) -> Session:
        """
        Crée et stocke une nouvelle session pour un utilisateur
        et la définit comme active.
        """
        session = Session(user)
        self.sessions[user.pseudo] = session
        self.current_session = session  # définit la session comme active
        return session

    def get_session(self, pseudo: str) -> Session | None:
        """
        Récupère la session active d'un utilisateur par pseudo.
        """
        session = self.sessions.get(pseudo)
        return session

    def get_active_session(self) -> Session | None:
        """
        Retourne la session actuellement active (définie par le dernier login)
        """
        return self.current_session

    def logout(self, pseudo: str):
        """
        Supprime la session de l'utilisateur et réinitialise
        la session active si nécessaire.
        """
        if pseudo in self.sessions:
            if self.current_session and self.current_session.user.pseudo == pseudo:
                self.current_session = None
            del self.sessions[pseudo]
