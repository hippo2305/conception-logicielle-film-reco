from unittest.mock import MagicMock

import pytest

from src.business_object.actor import Actor
from src.dao.actor_dao import ActorDAO


# =====================================================
# FIXTURE : ActorDAO avec DAO mocké
# =====================================================
@pytest.fixture
def actor_dao(monkeypatch):
    dao_mock = MagicMock()

    import src.dao.actor_dao as actor_dao_module

    # ActorDAO.__init__ fait self.dao = DAO()
    monkeypatch.setattr(actor_dao_module, "DAO", lambda: dao_mock)

    return ActorDAO()


@pytest.fixture
def sample_actor():
    return Actor(nom="DiCaprio", prenom="Leonardo")


# =====================================================
# exists()
# =====================================================
def test_exists_returns_false_when_none(actor_dao, sample_actor):
    actor_dao.dao.select_query.return_value = None
    assert actor_dao.exists(sample_actor) is False


def test_exists_returns_true_when_found(actor_dao, sample_actor):
    actor_dao.dao.select_query.return_value = (1,)
    assert actor_dao.exists(sample_actor) is True


def test_exists_returns_false_on_exception(actor_dao, sample_actor):
    actor_dao.dao.select_query.side_effect = Exception("DB error")
    assert actor_dao.exists(sample_actor) is False


# =====================================================
# add_actor()
# =====================================================
def test_add_actor_returns_false_if_exists(actor_dao, sample_actor):
    actor_dao.exists = MagicMock(return_value=True)

    res = actor_dao.add_actor(sample_actor)

    assert res is False
    actor_dao.dao.insert_query.assert_not_called()


def test_add_actor_inserts_and_returns_true_if_not_exists(actor_dao, sample_actor):
    actor_dao.exists = MagicMock(return_value=False)

    res = actor_dao.add_actor(sample_actor)

    assert res is True
    actor_dao.dao.insert_query.assert_called_once()


def test_add_actor_returns_false_on_exception(actor_dao, sample_actor):
    actor_dao.exists = MagicMock(return_value=False)
    actor_dao.dao.insert_query.side_effect = Exception("Insert error")

    assert actor_dao.add_actor(sample_actor) is False


# =====================================================
# get_id()
# IMPORTANT : ton code a un bug (ActorDAO().exists(actor))
# -> ça instancie un NOUVEL ActorDAO avec un NOUVEAU DAO.
# On contourne en patchant ActorDAO.exists au niveau de la classe.
# =====================================================
def test_get_id_returns_id_when_exists(actor_dao, sample_actor, monkeypatch):
    # Patch classe: ActorDAO().exists(actor) doit renvoyer True
    monkeypatch.setattr(ActorDAO, "exists", lambda _self, _actor: True)

    actor_dao.dao.select_query.return_value = (42,)
    assert actor_dao.get_id(sample_actor) == 42


def test_get_id_returns_true_when_actor_not_exists(
    actor_dao, sample_actor, monkeypatch
):
    # Selon TON code actuel, si l'acteur n'existe pas => return True (c'est bizarre mais on teste le comportement)
    monkeypatch.setattr(ActorDAO, "exists", lambda _self, _actor: False)

    res = actor_dao.get_id(sample_actor)
    assert res is True
    actor_dao.dao.select_query.assert_not_called()


def test_get_id_returns_none_on_exception(actor_dao, sample_actor, monkeypatch):
    monkeypatch.setattr(ActorDAO, "exists", lambda _self, _actor: True)
    actor_dao.dao.select_query.side_effect = Exception("Select error")

    assert actor_dao.get_id(sample_actor) is None


# =====================================================
# get_all_actors()
# =====================================================
def test_get_all_actors_returns_empty_list_when_none(actor_dao):
    actor_dao.dao.select_query.return_value = None
    assert actor_dao.get_all_actors() == []


def test_get_all_actors_builds_actor_objects(actor_dao):
    actor_dao.dao.select_query.return_value = [
        (1, "DiCaprio", "Leonardo"),
        (2, "Page", "Elliot"),
    ]

    actors = actor_dao.get_all_actors()

    assert len(actors) == 2
    assert actors[0].nom == "DiCaprio"
    assert actors[0].prenom == "Leonardo"


def test_get_all_actors_returns_none_on_exception(actor_dao):
    actor_dao.dao.select_query.side_effect = Exception("DB error")

    assert actor_dao.get_all_actors() is None


# =====================================================
# get_films()
# =====================================================
def test_get_films_returns_none_if_actor_not_exists(actor_dao, sample_actor):
    actor_dao.exists = MagicMock(return_value=False)

    assert actor_dao.get_films(sample_actor) is None
    actor_dao.dao.select_query.assert_not_called()


def test_get_films_returns_films_when_rows(actor_dao, sample_actor):
    actor_dao.exists = MagicMock(return_value=True)
    actor_dao.get_id = MagicMock(return_value=5)

    actor_dao.dao.select_query.return_value = [
        (1, "Inception", "Nolan", 2010, "Sci-Fi"),
        (2, "Memento", "Nolan", 2000, "Thriller"),
    ]

    films = actor_dao.get_films(sample_actor)

    assert films is not None
    assert len(films) == 2
    assert films[0].titre == "Inception"
    assert films[1].annee == 2000


def test_get_films_returns_none_if_no_rows(actor_dao, sample_actor):
    actor_dao.exists = MagicMock(return_value=True)
    actor_dao.get_id = MagicMock(return_value=5)

    actor_dao.dao.select_query.return_value = None
    assert actor_dao.get_films(sample_actor) is None


def test_get_films_returns_none_on_exception(actor_dao, sample_actor):
    actor_dao.exists = MagicMock(return_value=True)
    actor_dao.get_id = MagicMock(return_value=5)

    actor_dao.dao.select_query.side_effect = Exception("Select error")
    assert actor_dao.get_films(sample_actor) is None
