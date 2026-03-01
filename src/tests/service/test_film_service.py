from unittest.mock import MagicMock

import pytest

from src.business_object.actor import Actor
from src.business_object.film import Film
from src.service.film_service import FilmService


# =====================================================
# FIXTURE : FilmService avec dépendances mockées
# =====================================================
@pytest.fixture
def film_service(monkeypatch):
    tmdb_mock = MagicMock()
    film_dao_mock = MagicMock()

    # On patch les classes utilisées dans FilmService.__init__()
    import src.service.film_service as film_service_module

    monkeypatch.setattr(film_service_module, "TmdbService", lambda: tmdb_mock)
    monkeypatch.setattr(film_service_module, "FilmDAO", lambda: film_dao_mock)

    return FilmService()


@pytest.fixture
def sample_film():
    return Film(
        titre="Inception",
        realisateur="Nolan",
        annee=2010,
        genre="Sci-Fi",
        casting=[],
    )


@pytest.fixture
def sample_film_no_casting():
    # Film sans casting (None) pour tester les branches
    return Film(
        titre="Inception",
        realisateur="Nolan",
        annee=2010,
        genre="Sci-Fi",
        casting=None,
    )


# =====================================================
# instantiate_film()
# =====================================================
def test_instantiate_film_returns_film_object(film_service):
    film = film_service.instantiate_film(
        titre="Memento",
        realisateur="Nolan",
        annee=2000,
        genre="Thriller",
    )

    assert isinstance(film, Film)
    assert film.titre == "Memento"
    assert film.realisateur == "Nolan"
    assert film.annee == 2000
    assert film.genre == "Thriller"


# =====================================================
# add_casting()
# =====================================================
def test_add_casting_initializes_casting_if_none(film_service, sample_film_no_casting):
    actors = [Actor("DiCaprio", "Leonardo")]

    res = film_service.add_casting(sample_film_no_casting, actors)

    assert res is True
    assert sample_film_no_casting.casting == actors


def test_add_casting_adds_unique_actors(film_service, sample_film):
    actors = [Actor("DiCaprio", "Leonardo"), Actor("Page", "Elliot")]

    res = film_service.add_casting(sample_film, actors)

    assert res is True
    assert len(sample_film.casting) == 2
    assert actors[0] in sample_film.casting
    assert actors[1] in sample_film.casting


def test_add_casting_returns_false_on_duplicate_actor(film_service, sample_film):
    actor = Actor("DiCaprio", "Leonardo")
    sample_film.casting = [actor]

    # on essaie de rajouter le même
    res = film_service.add_casting(sample_film, [actor])

    assert res is False
    assert sample_film.casting == [actor]


# =====================================================
# get_casting()
# =====================================================
def test_get_casting_returns_existing_casting(film_service, sample_film):
    actor = Actor("DiCaprio", "Leonardo")
    sample_film.casting = [actor]

    res = film_service.get_casting(sample_film)

    assert res == [actor]
    film_service.film_dao.get_casting.assert_not_called()


def test_get_casting_fetches_from_dao_when_missing(
    film_service, sample_film_no_casting
):
    actor_list = [Actor("DiCaprio", "Leonardo")]
    film_service.film_dao.get_casting.return_value = actor_list

    res = film_service.get_casting(sample_film_no_casting)

    assert res == actor_list
    film_service.film_dao.get_casting.assert_called_once_with(sample_film_no_casting)


# =====================================================
# save_film()
# =====================================================
def test_save_film_calls_add_film_always(film_service, sample_film):
    res = film_service.save_film(sample_film)

    assert res is True
    film_service.film_dao.add_film.assert_called_once_with(sample_film)


def test_save_film_calls_add_casting_when_casting_present(film_service, sample_film):
    sample_film.casting = [Actor("DiCaprio", "Leonardo")]

    res = film_service.save_film(sample_film)

    assert res is True
    film_service.film_dao.add_film.assert_called_once_with(sample_film)
    film_service.film_dao.add_casting.assert_called_once_with(sample_film)


def test_save_film_does_not_call_add_casting_when_no_casting(
    film_service, sample_film_no_casting
):
    res = film_service.save_film(sample_film_no_casting)

    assert res is True
    film_service.film_dao.add_film.assert_called_once_with(sample_film_no_casting)
    film_service.film_dao.add_casting.assert_not_called()
