from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app_errors import (
    CreationError,
    IncorrectPasswordError,
    InvalidInputError,
    InvalidPassWordError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.business_object import User
from src.service.user_service import UserService


@pytest.fixture
def svc():
    """Fixture UserService avec DAO et utilitaires mockés."""
    service = UserService(user_dao=MagicMock())
    service.session_manager = MagicMock()
    service.current_session = None
    return service


# ---------- validate_email ---------------------------------------------- #
def test_validate_email_ok():
    """Email valide. Doit retourner True."""
    assert UserService.validate_email("a.b+test@example.com")


def test_validate_email_bad():
    """Email invalide. Doit retourner False."""
    assert not UserService.validate_email("not-an-email")


# ---------- signup ------------------------------------------------------ #
def test_signup_type_error(svc):
    """Signup avec type invalide. Devrait lever TypeError."""
    with pytest.raises(TypeError):
        svc.signup("not_a_user")


def test_signup_invalid_email(svc):
    """Signup avec email invalide. Devrait lever InvalidInputError."""
    user = MagicMock(spec=User)
    user.email = "bad"
    user.pseudo = "p"
    user._psswd = "Xy!23456"
    with pytest.raises(InvalidInputError):
        svc.signup(user)


def test_signup_pseudo_exists(svc):
    """Signup avec pseudo existant. Devrait lever UserAlreadyExistsError."""
    user = MagicMock(spec=User)
    user.email = "ok@ex.com"
    user.pseudo = "dupe"
    user._psswd = "Pwd!2345"
    svc.user_dao.get_user_by_pseudo.return_value = True
    with pytest.raises(UserAlreadyExistsError):
        svc.signup(user)


def test_signup_email_exists(svc):
    """Signup avec email existant. Devrait lever UserAlreadyExistsError."""
    user = MagicMock(spec=User)
    user.email = "dup@ex.com"
    user.pseudo = "unique"
    user._psswd = "Pwd!2345"
    svc.user_dao.get_user_by_pseudo.return_value = None
    svc.user_dao.get_all_users.return_value = [SimpleNamespace(email="dup@ex.com")]
    with pytest.raises(UserAlreadyExistsError):
        svc.signup(user)


def test_signup_bad_password(svc):
    """Signup avec mot de passe faible. Devrait lever InvalidPassWordError."""
    user = MagicMock(spec=User)
    user.email = "ok@ex.com"
    user.pseudo = "new"
    user._psswd = "weak"
    svc.user_dao.get_user_by_pseudo.return_value = None
    svc.user_dao.get_all_users.return_value = []
    fake_pp = MagicMock()
    fake_pp.validate_password.return_value = False
    with (
        patch("service.user_service.PasswordProcessing", return_value=fake_pp),
        pytest.raises(InvalidPassWordError),
    ):
        svc.signup(user)


def test_signup_success(svc):
    """Signup réussi. Retourne l'utilisateur."""
    user = MagicMock(spec=User)
    user.email = "ok@ex.com"
    user.pseudo = "new"
    user._psswd = "Strong!234"
    fake_pp = MagicMock()
    svc.user_dao.get_user_by_pseudo.return_value = None
    svc.user_dao.get_all_users.return_value = []
    svc.user_dao.create.return_value = True
    fake_pp = MagicMock()
    fake_pp.validate_password.return_value = True
    fake_pp._hash_password.return_value = b"hashed"

    with patch("service.user_service.PasswordProcessing", return_value=fake_pp):
        res = svc.signup(user)
        assert res is user


def test_signup_creation_fail_raises(svc):
    """Signup échoue à la création DAO. Devrait lever CreationError."""
    user = MagicMock(spec=User)
    user.email = "ok@ex.com"
    user.pseudo = "new2"
    user._psswd = "Strong!234"
    svc.user_dao.get_user_by_pseudo.return_value = None
    svc.user_dao.get_all_users.return_value = []
    svc.user_dao.create.return_value = False
    fake_pp = MagicMock()
    fake_pp.validate_password.return_value = True
    fake_pp._hash_password.return_value = b"hashed"

    with (
        patch("service.user_service.PasswordProcessing", return_value=fake_pp),
        pytest.raises(CreationError),
    ):
        svc.signup(user)


# ---------- login ------------------------------------------------------- #
def test_login_not_found(svc):
    """Login utilisateur inexistant. Devrait lever UserNotFoundError."""
    svc.user_dao.get_user_by_pseudo.return_value = None
    with pytest.raises(UserNotFoundError):
        svc.login("ghost", "pwd")


def test_login_bad_password(svc):
    """Login avec mot de passe incorrect. Devrait lever IncorrectPasswordError."""
    user_obj = SimpleNamespace(pseudo="u", is_active=True, _psswd="fakehash")
    svc.user_dao.get_user_by_pseudo.return_value = user_obj
    with (
        patch(
            "service.user_service.PasswordProcessing._verify_password",
            return_value=False,
        ),
        pytest.raises(IncorrectPasswordError),
    ):
        svc.login("u", "wrong")


def test_login_success(svc):
    """Login réussi. Retourne l'utilisateur et crée la session."""
    user_obj = SimpleNamespace(pseudo="u", _psswd="anystring", role="client")
    svc.user_dao.get_user_by_pseudo.return_value = user_obj
    fake_session = SimpleNamespace(user=user_obj, extend=lambda: None)

    with patch(
        "service.user_service.PasswordProcessing._verify_password",
        return_value=True,
    ):
        svc.session_manager.create_session.return_value = fake_session
        res = svc.login("u", "pwd")
        assert res == user_obj
        svc.session_manager.create_session.assert_called_once_with(user_obj)
