from typing import Literal
from unittest.mock import MagicMock, patch

import pytest

from src.business_object.user import User
from src.dao.user_dao import UserDao


# ---------------------- FIXTURES ---------------------- #


@pytest.fixture
def user_dao_with_mocks():
    """Fixture pour créer un UserDao avec des dépendances mockées"""
    with (
        patch("src.dao.user_dao.DAO") as mock_dao_class,
        patch("src.dao.user_dao.FilmDAO") as mock_film_dao_class,
    ):
        mock_dao_instance = MagicMock()
        mock_film_dao_instance = MagicMock()

        mock_dao_class.return_value = mock_dao_instance
        mock_film_dao_class.return_value = mock_film_dao_instance

        # Valeurs par défaut
        mock_dao_instance.select_query.return_value = None
        mock_dao_instance.insert_query.return_value = None

        dao = UserDao()

    return dao, mock_dao_instance, mock_film_dao_instance


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
        dao, mock_dao, _ = user_dao_with_mocks
        user, _, _ = user_examples

        # Act
        result = dao.create(user, role="client")

        # Assert
        assert result is True
        mock_dao.insert_query.assert_called_once()

    def test_create_success_admin(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        user_examples: tuple[User, User, User],
    ):
        """Test création réussie - admin"""
        # Arrange
        dao, mock_dao, _ = user_dao_with_mocks
        _, _, admin = user_examples

        # Act
        result = dao.create(admin, role="admin")

        # Assert
        assert result is True
        mock_dao.insert_query.assert_called_once()

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
        user_examples: tuple[User, User, User],
        role: Literal["client"] | Literal["admin"],
        expected_result: Literal[False],
        db_error: Exception,
    ):
        """Test échecs de création lors d'erreurs de base de données"""
        # Arrange
        dao, mock_dao, _ = user_dao_with_mocks
        user, _, _ = user_examples
        mock_dao.insert_query.side_effect = db_error

        # Act
        result = dao.create(user, role=role)

        # Assert
        assert result is expected_result
        mock_dao.insert_query.assert_called_once()

    def test_create_calls_insert_with_correct_args(
        self,
        user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock],
        user_examples: tuple[User, User, User],
    ):
        """Test que insert_query est appelé avec les bons arguments"""
        # Arrange
        dao, mock_dao, _ = user_dao_with_mocks
        user, _, _ = user_examples

        # Act
        result = dao.create(user, role="client")

        # Assert
        assert result is True
        call_args = mock_dao.insert_query.call_args[0]
        # Le premier argument doit être la table USERS
        assert call_args[0] == "USERS"


# ---------------------- TESTS change_user_email ---------------------- #


class TestChangeUserEmail:
    """Tests pour la méthode change_user_email() du UserDao"""

    def test_change_user_email_success(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test succès - email mis à jour avec succès"""
        # Arrange
        dao, mock_dao, _ = user_dao_with_mocks
        pseudo = "Bryan2025"
        new_email = "bryan.2025@new.com"

        # Act
        result = dao.change_user_email(pseudo, new_email)

        # Assert
        assert result is True
        mock_dao.update_query.assert_called_once()

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
        dao, mock_dao, _ = user_dao_with_mocks
        mock_dao.update_query.side_effect = db_error

        # Act
        result = dao.change_user_email("user1", "email@domain.com")

        # Assert
        assert result is False


# ---------------------- TESTS change_mdp ---------------------- #


class TestChangeMdp:
    """Tests pour la méthode change_mdp() du UserDao"""

    def test_change_mdp_success(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test succès - mot de passe mis à jour avec succès"""
        # Arrange
        dao, mock_dao, _ = user_dao_with_mocks
        pseudo = "Bryan2025"
        new_psswd = "NewBryan@2025"

        # Act
        result = dao.change_mdp(pseudo, new_psswd)

        # Assert
        assert result is True
        mock_dao.update_query.assert_called_once()

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
        dao, mock_dao, _ = user_dao_with_mocks
        mock_dao.update_query.side_effect = db_error

        # Act
        result = dao.change_mdp("Viki2025", "VikiPass@2025")

        # Assert
        assert result is False


# ---------------------- TESTS delete_user ---------------------- #


class TestDeleteUser:
    """Tests pour la méthode delete_user() du UserDao"""

    def test_delete_user_success(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test succès - suppression réussie"""
        # Arrange
        dao, mock_dao, _ = user_dao_with_mocks
        pseudo = "user_to_delete"

        # Act
        result = dao.delete_user(pseudo)

        # Assert
        assert result is True
        mock_dao.del_query.assert_called_once()

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
        """Test - erreur lors de la suppression d'un utilisateur"""
        # Arrange
        dao, mock_dao, _ = user_dao_with_mocks
        mock_dao.del_query.side_effect = db_error

        # Act
        result = dao.delete_user("user_to_delete")

        # Assert
        assert result is False


# ---------------------- TESTS get_all_users ---------------------- #


class TestGetAllUsers:
    """Tests pour la méthode get_all_users() du UserDao"""

    def test_get_all_users_returns_list(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test récupération réussie des utilisateurs"""
        dao, mock_dao, _ = user_dao_with_mocks

        # select_query avec multiple=True retourne une liste de tuples
        # format : (id, pseudo, email, psswd, role)
        mock_dao.select_query.return_value = [
            (1, "Viki2025", "viki@example.com", "VikiPass@123", "client"),
            (2, "Bryan2025", "bryan@example.com", "BryanPass@123", "admin"),
        ]

        result = dao.get_all_users()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].pseudo == "Viki2025"
        assert result[1].pseudo == "Bryan2025"
        mock_dao.select_query.assert_called_once()

    def test_get_all_users_returns_none_when_empty(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test retourne None quand aucun utilisateur"""
        dao, mock_dao, _ = user_dao_with_mocks
        mock_dao.select_query.return_value = None

        result = dao.get_all_users()

        assert result is None
        mock_dao.select_query.assert_called_once()

    def test_get_all_users_database_error(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test échec lors d'une erreur de base de données"""
        dao, mock_dao, _ = user_dao_with_mocks
        mock_dao.select_query.side_effect = Exception("DB crash")

        result = dao.get_all_users()

        assert result is None


# ---------------------- TESTS get_by_pseudo ---------------------- #


class TestGetByPseudo:
    """Tests pour la méthode get_by_pseudo() du UserDao"""

    def test_get_by_pseudo_client(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test récupération d'un client"""
        dao, mock_dao, _ = user_dao_with_mocks

        # format : (id, pseudo, email, psswd, role)
        mock_dao.select_query.return_value = (
            1,
            "Viki2025",
            "viki@example.com",
            "VikiPass@123",
            "client",
        )

        result = dao.get_by_pseudo("Viki2025")

        assert result is not None
        assert result.pseudo == "Viki2025"
        mock_dao.select_query.assert_called_once()

    def test_get_by_pseudo_admin(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test récupération d'un admin"""
        dao, mock_dao, _ = user_dao_with_mocks

        mock_dao.select_query.return_value = (
            2,
            "Bryan2025",
            "bryan@example.com",
            "BryanPass@123",
            "admin",
        )

        result = dao.get_by_pseudo("Bryan2025")

        assert result is not None
        assert result.pseudo == "Bryan2025"

    def test_get_by_pseudo_not_found(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test aucun utilisateur trouvé"""
        dao, mock_dao, _ = user_dao_with_mocks
        mock_dao.select_query.return_value = None

        result = dao.get_by_pseudo("Louis25")

        assert result is None

    def test_get_by_pseudo_database_error(
        self, user_dao_with_mocks: tuple[UserDao, MagicMock, MagicMock]
    ):
        """Test échec lors d'une erreur de base de données"""
        dao, mock_dao, _ = user_dao_with_mocks
        mock_dao.select_query.side_effect = Exception("Erreur SQL")

        result = dao.get_by_pseudo("Louis25")

        assert result is None
