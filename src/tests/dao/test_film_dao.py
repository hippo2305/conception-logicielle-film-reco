from unittest.mock import MagicMock

import pytest

from src.business_object.actor import Actor
from src.business_object.film import Film
from src.dao.film_dao import FilmDAO


# =====================================================
# FIXTURE : FilmDAO avec DAO et ActorDAO mockés
# =====================================================
@pytest.fixture
def film_dao(monkeypatch):
    dao_mock = MagicMock()
    actor_dao_mock = MagicMock()

    import src.dao.film_dao as film_dao_module

    monkeypatch.setattr(film_dao_module, "DAO", lambda: dao_mock)
    monkeypatch.setattr(film_dao_module, "ActorDAO", lambda: actor_dao_mock)

    return FilmDAO()


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
def sample_casting_film():
    return Film(
        titre="Inception",
        realisateur="Nolan",
        annee=2010,
        genre="Sci-Fi",
        casting=[
            Actor("DiCaprio", "Leonardo"),
            Actor("Page", "Elliot"),
        ],
    )


# =====================================================
# exists()
# =====================================================
def test_exists_returns_false_when_none(film_dao, sample_film):
    film_dao.dao.select_query.return_value = None
    assert film_dao.exists(sample_film) is False


def test_exists_returns_true_when_found(film_dao, sample_film):
    film_dao.dao.select_query.return_value = (1,)
    assert film_dao.exists(sample_film) is True


def test_exists_returns_false_on_exception(film_dao, sample_film):
    film_dao.dao.select_query.side_effect = Exception("DB error")
    assert film_dao.exists(sample_film) is False


# =====================================================
# add_film()
# =====================================================
def test_add_film_returns_false_if_exists(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=True)

    result = film_dao.add_film(sample_film)

    assert result is False
    film_dao.dao.insert_query.assert_not_called()


def test_add_film_inserts_if_not_exists(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=False)

    result = film_dao.add_film(sample_film)

    assert result is None  # ton code ne retourne rien en succès
    film_dao.dao.insert_query.assert_called_once()


def test_add_film_returns_false_on_exception(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=False)
    film_dao.dao.insert_query.side_effect = Exception("Insert error")

    assert film_dao.add_film(sample_film) is False


# =====================================================
# get_id()
# =====================================================
def test_get_id_returns_none_if_not_exists(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=False)

    assert film_dao.get_id(sample_film) is None


def test_get_id_returns_id_if_exists(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=True)
    film_dao.dao.select_query.return_value = (42,)

    assert film_dao.get_id(sample_film) == 42


def test_get_id_returns_none_on_exception(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=True)
    film_dao.dao.select_query.side_effect = Exception("Error")

    assert film_dao.get_id(sample_film) is None


# =====================================================
# get_all_films()
# =====================================================
def test_get_all_films_empty(film_dao):
    film_dao.dao.select_query.return_value = None
    assert film_dao.get_all_films() == []


def test_get_all_films_builds_objects(film_dao):
    film_dao.dao.select_query.return_value = [
        (1, "Inception", "Nolan", 2010, "Sci-Fi"),
        (2, "Memento", "Nolan", 2000, "Thriller"),
    ]

    films = film_dao.get_all_films()

    assert len(films) == 2
    assert films[0].titre == "Inception"
    assert films[1].annee == 2000


# =====================================================
# get_casting()
# =====================================================
def test_get_casting_returns_none_if_not_exists(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=False)
    assert film_dao.get_casting(sample_film) is None


def test_get_casting_returns_actors(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=True)
    film_dao.get_id = MagicMock(return_value=10)

    film_dao.dao.select_query.return_value = [
        (1, "DiCaprio", "Leonardo"),
        (2, "Page", "Elliot"),
    ]

    actors = film_dao.get_casting(sample_film)

    assert len(actors) == 2
    assert actors[0].nom == "DiCaprio"
    assert actors[1].prenom == "Elliot"


def test_get_casting_returns_none_if_empty(film_dao, sample_film):
    film_dao.exists = MagicMock(return_value=True)
    film_dao.get_id = MagicMock(return_value=10)

    film_dao.dao.select_query.return_value = None
    assert film_dao.get_casting(sample_film) is None


# =====================================================
# add_casting()
# =====================================================
def test_add_casting_inserts_when_missing(film_dao, sample_casting_film):
    film_dao.get_id = MagicMock(return_value=99)

    film_dao.actor_dao.exists.side_effect = [False, False]
    film_dao.actor_dao.get_id.side_effect = [1, 2]

    film_dao.dao.select_query.return_value = None

    result = film_dao.add_casting(sample_casting_film)

    assert result is True
    assert film_dao.actor_dao.add_actor.call_count == 2


def test_add_casting_skips_existing_association(film_dao, sample_casting_film):
    film_dao.get_id = MagicMock(return_value=99)

    film_dao.actor_dao.exists.side_effect = [True, True]
    film_dao.actor_dao.get_id.side_effect = [1, 2]

    film_dao.dao.select_query.return_value = (1,)

    result = film_dao.add_casting(sample_casting_film)

    assert result is True


def test_add_casting_returns_none_if_no_casting(film_dao, sample_film):
    film_dao.get_id = MagicMock(return_value=99)
    assert film_dao.add_casting(sample_film) is None


# =====================================================
# genre_list / list_id
# =====================================================
def test_genre_list(film_dao):
    film_dao.dao.select_query.return_value = [("SCI-FI",), ("DRAMA",)]
    assert film_dao.genre_list() == ["SCI-FI", "DRAMA"]


def test_list_id(film_dao):
    film_dao.dao.select_query.return_value = [(1,), (2,), (3,)]
    assert film_dao.list_id() == [1, 2, 3]


# =====================================================
# get_by_id()
# =====================================================
def test_get_by_id_returns_none(film_dao):
    film_dao.dao.select_query.return_value = None
    assert film_dao.get_by_id("10") is None


def test_get_by_id_returns_film(film_dao):
    film_dao.dao.select_query.return_value = (
        10,
        "Inception",
        "Nolan",
        2010,
        "Sci-Fi",
    )

    film = film_dao.get_by_id("10")

    assert film.titre == "Inception"
    assert film.realisateur == "Nolan"
    assert film.annee == 2010
    assert film.genre == "Sci-Fi"
