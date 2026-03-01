from unittest.mock import MagicMock

import pytest

from src.business_object.actor import Actor
from src.business_object.film import Film
from src.service.actor_service import ActorService


# =====================================================
# FIXTURE : ActorService avec ActorDAO mocké
# =====================================================
@pytest.fixture
def actor_service(monkeypatch):
    actor_dao_mock = MagicMock()

    # Patch du symbole ActorDAO dans le module testé
    import src.service.actor_service as actor_service_module

    monkeypatch.setattr(actor_service_module, "ActorDAO", lambda: actor_dao_mock)

    return ActorService()


@pytest.fixture
def sample_actor():
    return Actor(nom="DiCaprio", prenom="Leonardo")


# =====================================================
# instantiate_actor()
# =====================================================
def test_instantiate_actor_returns_actor(actor_service):
    actor = actor_service.instantiate_actor(nom="Page", prenom="Elliot")

    assert isinstance(actor, Actor)
    assert actor.nom == "Page"
    assert actor.prenom == "Elliot"


# =====================================================
# get_films()
# =====================================================
def test_get_films_calls_dao(actor_service, sample_actor):
    films = [
        Film(titre="Inception", realisateur="Nolan", annee=2010, genre="Sci-Fi"),
        Film(titre="Memento", realisateur="Nolan", annee=2000, genre="Thriller"),
    ]
    actor_service._actor_dao.get_films.return_value = films

    res = actor_service.get_films(sample_actor)

    assert res == films
    actor_service._actor_dao.get_films.assert_called_once_with(sample_actor)


# =====================================================
# save_actor()
# =====================================================
def test_save_actor_returns_true_when_insert_ok(actor_service, sample_actor):
    actor_service._actor_dao.add_actor.return_value = True

    res = actor_service.save_actor(sample_actor)

    assert res is True
    actor_service._actor_dao.add_actor.assert_called_once_with(sample_actor)


def test_save_actor_returns_false_when_insert_fails(actor_service, sample_actor):
    actor_service._actor_dao.add_actor.return_value = False

    res = actor_service.save_actor(sample_actor)

    assert res is False
    actor_service._actor_dao.add_actor.assert_called_once_with(sample_actor)
