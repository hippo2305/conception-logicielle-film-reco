import bcrypt

from dao.user_dao import UserDao


class AuthService:
    def __init__(self):
        self.user_dao = UserDao()

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def signup(self, pseudo: str, password: str, email: str | None = None) -> None:
        if self.user_dao.get_user_row_by_pseudo(pseudo):
            raise ValueError("Ce pseudo existe déjà.")
        self.user_dao.create_minimal(
            pseudo=pseudo,
            password_hash=self.hash_password(password),
            email=email,
            role="client",
            listfilms="[]",
        )

    def login(self, pseudo: str, password: str) -> dict:
        row = self.user_dao.get_user_row_by_pseudo(pseudo)
        if not row or not self.verify_password(password, row["password"]):
            raise ValueError("Identifiants invalides.")
        return {"id_user": row["id_user"], "pseudo": row["pseudo"], "role": row["role"]}
