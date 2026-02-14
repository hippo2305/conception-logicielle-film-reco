from typing import Literal
from unittest.mock import MagicMock, patch

import pytest

from src.business_object import User
from src.dao.user_dao import UserDao


# ---------------------- FIXTURES ---------------------- #


@pytest.fixture
def user_dao_with_mocks():
    """Fixture pour créer un UserDao avec des dépendances mockées"""
    mock_db_conn = MagicMock()
    mock_cursor = MagicMock()

    # Configuration du contexte du cursor
    mock_db_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_db_conn.cursor.return_value.__exit__.return_value = None
    mock_db_conn.connection = mock_db_conn

    # Initialize fetchall and fetchone with default empty values
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None

    with (
        patch("dao.user_dao.DBConnection") as mock_db_class,
    ):
        mock_db_instance = MagicMock()
        mock_db_instance.connection = mock_db_conn
        mock_db_class.return_value = mock_db_instance
        dao = UserDao()
    return dao, mock_db_conn, mock_cursor


@pytest.fixture
def user_examples():
    """Fixture avec différents exemples d'utilisateurs"""
    user = User(
        pseudo="louis-29",
        email="louis.toe@gmail.com",
        psswd="DemainJeNeFeraiPasInfo@15",
        listfilms=[],
    )

    user_wrong_psswd = User(
        pseudo="louis-29-55",
        email="louis55.toe@gmail.com",
        psswd="DemainJeNeFeraiPasInfo",
        listfilms=[],
    )

    admin_user = User(
        pseudo="admin-Viki",
        email="admin@example.com",
        psswd="AdminViki@2025",
        listfilms=["Aladin", "Le Roi Lion"],
    )

    return user, user_wrong_psswd, admin_user


# ---------------------- TEST create ---------------------- #


class TestCreate:
    """Tests pour la méthode create() du UserDao"""

    def test_create_success_client(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        user_examples: tuple[User, User, User],
    ):
        """Test création réussie - client avec rôle par défaut"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        user, _, _ = user_examples

        # Act
        result = dao.create(user, role="client")

        # Assert
        assert result is True
        mock_cursor.execute.assert_called_once()
        _, values_call = mock_cursor.execute.call_args[0]
        assert values_call[4] == "client"
        mock_conn.commit.assert_called_once()

    def test_create_success_admin(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        user_examples: tuple[User, User, User],
    ):
        """Test création réussie - admin"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        _, _, admin = user_examples

        # Act
        result = dao.create(admin, role="admin")

        # Assert
        assert result is True
        _, values_call = mock_cursor.execute.call_args[0]
        assert values_call[4] == "admin"
        mock_conn.commit.assert_called_once()

    @pytest.mark.parametrize(
        "role, expected_result, db_error",
        [
            # Échec - erreur de connexion DB
            ("client", False, Exception("Connection timeout")),
            # Échec - violation de contrainte unique
            (
                "client",
                False,
                Exception("duplicate key value violates unique constraint"),
            ),
            # Échec - erreur réseau
            ("admin", False, Exception("Network error")),
        ],
    )
    def test_create_database_errors(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        user_examples: tuple[User, User, User, User],
        role: Literal["client"] | Literal["admin"],
        expected_result: Literal[False],
        db_error: Exception,
    ):
        """Test échecs de création lors d'erreurs de base de données"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        user, _, _ = user_examples
        mock_cursor.execute.side_effect = db_error

        # Act
        result = dao.create(user, role=role)

        # Assert
        assert result is expected_result
        mock_cursor.execute.assert_called_once()
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
        assert "Erreur lors de l'insertion"

        # Vérification de la requête SQL
        sql_call, values_call = mock_cursor.execute.call_args[0]
        assert "INSERT INTO users" in sql_call
        assert values_call[0] == user.pseudo
        assert values_call[1] == user.email
        assert values_call[2] == user.psswd
        assert values_call[3] == user.listfilms
        assert values_call[4] == role

        # Vérification commit/rollback
        if expected_result:
            mock_conn.commit.assert_called_once()
            mock_conn.rollback.assert_not_called()
        else:
            mock_conn.rollback.assert_called_once()
            mock_conn.commit.assert_not_called()
            assert "Erreur lors de l'insertion"

    def test_create_verifies_all_required_fields(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        user_examples: tuple[User, User, User],
    ):
        """Test que tous les champs requis sont présents dans la requête SQL"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        user, _, _ = user_examples

        # Act
        result = dao.create(user, role="premium")

        # Assert
        assert result is True
        sql_call, values_call = mock_cursor.execute.call_args[0]

        required_fields = [
            "pseudo",
            "email",
            "password",
            "listfilms",
            "role",
        ]
        for field in required_fields:
            assert field in sql_call, (
                f"Le champ '{field}' doit être présent dans la requête SQL"
            )

        assert len(values_call) == 5


# ---------------------- TESTS change_user_email ---------------------- #


class TestChangeUserEmail:
    """Tests pour la méthode change_user_email() du UserDao"""

    def test_change_user_email_success(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test succès - email mis à jour avec succès"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        pseudo = "Bryan2025"
        new_email = "bryan.2025@new.com"
        mock_cursor.rowcount = 1

        # Act
        result = dao.change_user_email(pseudo, new_email)

        # Assert
        assert result is True
        sql_call, values_call = mock_cursor.execute.call_args[0]
        assert "UPDATE users SET email" in sql_call
        assert values_call == (new_email, pseudo)
        mock_conn.commit.assert_called_once()

    def test_change_user_email_no_update(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test - aucun utilisateur mis à jour (pseudo inexistant)"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        mock_cursor.rowcount = 0

        # Act
        result = dao.change_user_email("ghost_user", "ghost@example.com")

        # Assert
        assert result is False
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @pytest.mark.parametrize(
        "db_error",
        [
            Exception("Connection dropped"),
            Exception("Duplicate email address"),
            Exception("Invalid SQL operation"),
        ],
    )
    def test_change_user_email_database_error(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        db_error: Exception,
    ):
        """Test - erreur lors de la mise à jour de l'email"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        mock_cursor.execute.side_effect = db_error

        # Act
        result = dao.change_user_email("user1", "email@domain.com")

        # Assert
        assert result is False
        mock_conn.rollback.assert_called_once()
        assert "Erreur lors du changement d'email"


# ---------------------- TESTS change_mdp ---------------------- #


class TestChangeMdp:
    """Tests pour la méthode change_mdp() du UserDao"""

    def test_change_mdp_success(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test succès - mot de passe mis à jour avec succès"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        pseudo = "Bryan2025"
        new_psswd = "NewBryan@2025"
        mock_cursor.rowcount = 1

        # Act
        result = dao.change_mdp(pseudo, new_psswd)

        # Assert
        assert result is True
        sql_call, values_call = mock_cursor.execute.call_args[0]
        assert "UPDATE users SET password" in sql_call
        assert values_call == (new_psswd, pseudo)
        mock_conn.commit.assert_called_once()

    def test_change_mdp_no_update(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test - aucun utilisateur mis à jour (pseudo inexistant)"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        mock_cursor.rowcount = 0

        # Act
        result = dao.change_mdp("unknown_user", "SomePassword@123")

        # Assert
        assert result is False
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @pytest.mark.parametrize(
        "db_error",
        [
            Exception("Database connection lost"),
            Exception("Invalid SQL syntax"),
            Exception("Write permission denied"),
        ],
    )
    def test_change_mdp_database_error(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        db_error: Exception,
    ):
        """Test - erreur lors de la mise à jour du mot de passe"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        mock_cursor.execute.side_effect = db_error

        # Act
        result = dao.change_mdp("Viki2025", "VikiPass@2025")

        # Assert
        assert result is False
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
        assert "Erreur lors du changement du mot de passe"


# ---------------------- TESTS delete_user ---------------------- #


class TestDeleteUser:
    """Tests pour la méthode delete_user() du UserDao"""

    def test_delete_user_success(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test succès - suppression réussie"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        pseudo = "user_to_delete"
        mock_cursor.rowcount = 1

        # Act
        result = dao.delete_user(pseudo)

        # Assert
        assert result is True
        sql_call, values_call = mock_cursor.execute.call_args[0]
        assert "DELETE FROM users" in sql_call
        assert values_call == (pseudo,)
        mock_conn.commit.assert_called_once()

    def test_delete_user_no_match(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test - suppression sans correspondance (aucun utilisateur trouvé)"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        mock_cursor.rowcount = 0

        # Act
        result = dao.delete_user("ghost_user")

        # Assert
        assert result is False
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @pytest.mark.parametrize(
        "db_error",
        [
            Exception("Database unreachable"),
            Exception("Foreign key constraint violation"),
            Exception("Transaction aborted"),
        ],
    )
    def test_delete_user_database_error(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        db_error: Exception,
    ):
        """Test - erreur lors de la suppression d’un utilisateur"""
        # Arrange
        dao, mock_conn, mock_cursor = user_dao_with_mocks
        mock_cursor.execute.side_effect = db_error

        # Act
        result = dao.delete_user("user_to_delete")

        # Assert
        assert result is False
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()


# ---------------------- TESTS get_all_users ---------------------- #


class TestGetAllUsers:
    """Tests pour la méthode get_all_users() du UserDao"""

    def test_get_all_users_returns_list(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test récupération réussie des utilisateurs"""
        dao, mock_db_conn, mock_cursor = user_dao_with_mocks

        mock_cursor.fetchall.return_value = [
            {
                "pseudo": "Viki2025",
                "email": "viki@example.com",
                "password": "VikiPass@123",
                "listfilms": [],
                "role": "client",
            },
            {
                "pseudo": "Bryan2025",
                "email": "bryan@example.com",
                "password": "BryanPass@123",
                "listfilms": [],
                "role": "admin",
            },
        ]

        result = dao.get_all_users()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].pseudo == "Viki2025"
        assert result[1].pseudo == "Bryan2025"
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users;")

    def test_get_all_users_returns_none_when_empty(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test retourne None quand aucun utilisateur"""
        dao, mock_db_conn, mock_cursor = user_dao_with_mocks

        mock_cursor.fetchall.return_value = []

        result = dao.get_all_users()

        assert result == []
        mock_cursor.execute.assert_called_once()

    def test_get_all_users_database_error(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test échec lors d'une erreur de base de données"""
        dao, mock_db_conn, mock_cursor = user_dao_with_mocks

        mock_cursor.execute.side_effect = Exception("DB crash")

        result = dao.get_all_users()

        assert result == []


# ---------------------- TESTS get_user_by_pseudo ---------------------- #


class TestGetUserByPseudo:
    """Tests pour la méthode get_user_by_pseudo() du UserDao"""

    def test_get_user_by_pseudo_client(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test récupération d’un client"""
        dao, mock_db_conn, mock_cursor = user_dao_with_mocks

        mock_cursor.fetchone.return_value = {
            "pseudo": "Viki2025",
            "email": "viki@example.com",
            "password": "VikiPass@123",
            "listfilms": None,
            "role": "client",
        }

        result = dao.get_user_by_pseudo("Viki2025")

        assert result is not None
        assert result.pseudo == "Viki2025"
        assert result.role == "client"
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE pseudo = %s;", ("Viki2025",)
        )

    def test_get_user_by_pseudo_admin(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test récupération d’un admin"""
        dao, mock_db_conn, mock_cursor = user_dao_with_mocks

        mock_cursor.fetchone.return_value = {
            "pseudo": "Bryan2025",
            "email": "bryan@example.com",
            "password": "BryanPass@123",
            "listfilms": [],
            "role": "admin",
        }

        result = dao.get_user_by_pseudo("Bryan2025")

        assert result is not None
        assert result.pseudo == "Bryan2025"
        assert result.role == "admin"

    def test_get_user_by_pseudo_not_found(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test aucun utilisateur trouvé"""
        dao, mock_db_conn, mock_cursor = user_dao_with_mocks

        mock_cursor.fetchone.return_value = None

        result = dao.get_user_by_pseudo("Louis25")

        assert result is None

    def test_get_user_by_pseudo_database_error(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test échec lors d'une erreur de base de données"""
        dao, mock_db_conn, mock_cursor = user_dao_with_mocks

        mock_cursor.execute.side_effect = Exception("Erreur SQL")

        result = dao.get_user_by_pseudo("Louis25")

        assert result is None
