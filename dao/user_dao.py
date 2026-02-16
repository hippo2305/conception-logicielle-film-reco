from __future__ import annotations

import logging

from business_object import Admin, Client, User
from dao.db_connection import get_connection


class UserDao:
    """
    DAO SQLite pour la table 'users'.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create(self, user: User, role: str = "client") -> bool:
        sql = """
            INSERT INTO users (pseudo, email, listfilms, password, role)
            VALUES (?, ?, ?, ?, ?);
        """

        values = (
            user.pseudo,
            getattr(user, "email", None),
            getattr(user, "listfilms", "[]"),
            user.psswd,  # hash
            role,
        )

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, values)
            return True
        except Exception:
            self.logger.exception("Erreur lors de l'insertion user")
            return False

    def create_minimal(
        self,
        pseudo: str,
        password_hash: str,
        email: str | None = None,
        role: str = "client",
        listfilms: str = "[]",
    ) -> bool:
        sql = """
            INSERT INTO users (pseudo, email, listfilms, password, role)
            VALUES (?, ?, ?, ?, ?);
        """
        values = (pseudo, email, listfilms, password_hash, role)

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, values)
            return True
        except Exception:
            self.logger.exception("Erreur lors de la création user (minimal)")
            return False

    def get_user_row_by_pseudo(self, pseudo: str) -> dict | None:
        sql = "SELECT * FROM users WHERE LOWER(pseudo) = LOWER(?) LIMIT 1;"

        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, (pseudo,))
                row = cur.fetchone()
            return dict(row) if row else None
        except Exception:
            self.logger.exception("Erreur get_user_row_by_pseudo")
            return None

    def login(self, pseudo: str) -> Client | Admin | None:
        res = self.get_user_row_by_pseudo(pseudo)
        if not res:
            return None

        if res["role"] == "client":
            return Client(
                pseudo=res["pseudo"],
                email=res.get("email"),
                psswd=res["password"],
                listfilms=res.get("listfilms", "[]"),
                role=res["role"],
            )

        return Admin(
            pseudo=res["pseudo"],
            email=res.get("email"),
            psswd=res["password"],
            listfilms=res.get("listfilms", "[]"),
            role=res["role"],
        )
