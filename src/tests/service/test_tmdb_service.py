from unittest.mock import MagicMock

import pytest
import requests

from src.business_object.film import Film
from src.service.tmdb_service import TmdbService


# =====================================================
# Fixtures
# =====================================================
@pytest.fixture
def tmdb_service(monkeypatch):
    # Pas besoin d'une vraie clé
    monkeypatch.setenv("TMDB_API_KEY", "fake_key")
    # Base URL stable (évite surprises)
    monkeypatch.setenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    return TmdbService()


@pytest.fixture
def mock_requests_get(monkeypatch):
    """
    Patch requests.get dans le module src.service.tmdb_service
    """
    mock_get = MagicMock()
    import src.service.tmdb_service as tmdb_module

    monkeypatch.setattr(tmdb_module.requests, "get", mock_get)
    return mock_get


# =====================================================
# __init__
# =====================================================
def test_init_raises_when_api_key_missing(monkeypatch):
    monkeypatch.setenv("TMDB_API_KEY", "")
    monkeypatch.setenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")

    with pytest.raises(RuntimeError, match="Clé TMDB_API_KEY manquante"):
        TmdbService()


# =====================================================
# _get()
# =====================================================
def test__get_returns_json(tmdb_service, mock_requests_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"ok": True}
    mock_requests_get.return_value = mock_response

    res = tmdb_service._get("/test")

    assert res == {"ok": True}
    mock_requests_get.assert_called_once()

    # Vérifie qu'on envoie bien api_key + language par défaut
    _, kwargs = mock_requests_get.call_args
    assert kwargs["timeout"] == 20
    assert kwargs["params"]["api_key"] == "fake_key"
    assert kwargs["params"]["language"] == "fr-FR"


def test__get_merges_extra_params(tmdb_service, mock_requests_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"ok": True}
    mock_requests_get.return_value = mock_response

    tmdb_service._get("/test", extra_params={"query": "abc", "page": 2})

    _, kwargs = mock_requests_get.call_args
    assert kwargs["params"]["api_key"] == "fake_key"
    assert kwargs["params"]["language"] == "fr-FR"
    assert kwargs["params"]["query"] == "abc"
    assert kwargs["params"]["page"] == 2


def test__get_raises_http_error(tmdb_service, mock_requests_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("boom")
    mock_requests_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        tmdb_service._get("/test")


# =====================================================
# search_movie / movie_details / movie_credits
# =====================================================
def test_search_movie_calls__get(tmdb_service):
    tmdb_service._get = MagicMock(return_value={"results": []})

    res = tmdb_service.search_movie(query="Inception", page=2)

    assert res == {"results": []}
    tmdb_service._get.assert_called_once_with(
        "/search/movie",
        {"query": "Inception", "page": 2},
    )


def test_movie_details_calls__get(tmdb_service):
    tmdb_service._get = MagicMock(return_value={"id": 10})

    res = tmdb_service.movie_details(movie_id=10)

    assert res == {"id": 10}
    tmdb_service._get.assert_called_once_with("/movie/10")


def test_movie_credits_calls__get(tmdb_service):
    tmdb_service._get = MagicMock(return_value={"cast": []})

    res = tmdb_service.movie_credits(movie_id=10)

    assert res == {"cast": []}
    tmdb_service._get.assert_called_once_with(
        "/movie/10/credits",
        {"language": None},
    )


# =====================================================
# get_movie_filtered()
# =====================================================
def test_get_movie_filtered_returns_film(tmdb_service):
    tmdb_service.search_movie = MagicMock(return_value={"results": [{"id": 42}]})
    tmdb_service.movie_details = MagicMock(
        return_value={
            "title": "Inception",
            "release_date": "2010-07-16",
            "genres": [{"name": "Science Fiction"}, {"name": "Action"}],
        }
    )
    tmdb_service.movie_credits = MagicMock(
        return_value={
            "crew": [{"job": "Director", "name": "Christopher Nolan"}],
            "cast": [
                {"name": "Actor 1"},
                {"name": "Actor 2"},
                {"name": "Actor 3"},
            ],
        }
    )

    film = tmdb_service.get_movie_filtered(query="Inception", nb_acteurs=2)

    assert isinstance(film, Film)
    assert film.titre == "Inception"
    assert film.realisateur == "Christopher Nolan"
    assert film.annee == 2010
    assert film.genre == "Science Fiction, Action"
    assert film.casting == ["Actor 1", "Actor 2"]


def test_get_movie_filtered_raises_when_no_results(tmdb_service):
    tmdb_service.search_movie = MagicMock(return_value={"results": []})

    with pytest.raises(ValueError, match="Aucun film trouvé"):
        tmdb_service.get_movie_filtered(query="Nope", nb_acteurs=2)


def test_get_movie_filtered_handles_missing_release_date(tmdb_service):
    tmdb_service.search_movie = MagicMock(return_value={"results": [{"id": 1}]})
    tmdb_service.movie_details = MagicMock(
        return_value={
            "title": "Test",
            "release_date": None,
            "genres": [],
        }
    )
    tmdb_service.movie_credits = MagicMock(return_value={"crew": [], "cast": []})

    film = tmdb_service.get_movie_filtered(query="Test", nb_acteurs=5)

    assert film.titre == "Test"
    assert film.realisateur is None
    assert film.annee is None
    assert film.genre == ""
    assert film.casting == []
