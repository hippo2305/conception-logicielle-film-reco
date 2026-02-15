import uuid

import dotenv

from src.business_object.user import User


dotenv.load_dotenv()


class Session:
    """
    Représente une session utilisateur unique.

    Attributs
    ---------
    session_id : str
        Identifiant unique de la session.
    user : User
        L'utilisateur associé à la session.
    """

    def __init__(
        self,
        user: User,
    ):
        self.session_id: str = str(uuid.uuid4())  # ID unique pour chaque session
        self.user: User = user
