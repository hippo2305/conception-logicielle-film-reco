from __future__ import annotations

import os

from fastapi import FastAPI, Query
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from starlette.status import HTTP_303_SEE_OTHER
import uvicorn

from src.client.film_client import FilmClient
from src.client.user_client import UserClient
from src.dao.dao import DAO


ROOT_PATH = os.getenv("ROOT_PATH", "/proxy/8000")  # "" en local si besoin

app = FastAPI(root_path=ROOT_PATH, title="MovieReco API")

dao = DAO()
user_client = UserClient()
film_client = FilmClient()

# ============================================================
# Swagger: enlever les réponses 422 "Validation Error" dans /docs
# ============================================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes,
        description=app.description,
    )

    for path in schema.get("paths", {}).values():
        for method in path.values():
            responses = method.get("responses", {})
            responses.pop("422", None)

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================
# Models
# ============================================================
class ErrorResponse(BaseModel):
    error: str


class SignupResponse(BaseModel):
    status: str = "ok"
    pseudo: str


class FavoriteAddResponse(BaseModel):
    status: str = "ok"
    titre: str
    realisateur: str
    annee: str
    annee: int | None = None


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs", status_code=HTTP_303_SEE_OTHER)


# ============================================================
# AUTH helper
# ============================================================


# ============================================================
# USERS
# ============================================================
@app.post(
    "/users/signup",
    response_model=SignupResponse,
    responses={400: {"model": ErrorResponse}},
)
def signup(
    pseudo: str = Query(...),
    email: str = Query(...),
    password: str = Query(...),
):
    return user_client.signup(pseudo, email, password)


# ============================================================
# TMDB (PUBLIC) - recherche live
# ============================================================

@app.get("/tmdb/movie")
def tmdb_movie_details(
    titre: str = Query(...),
):
    return film_client.get_film_tmdb(titre)


"""
# ============================================================
# FILMS (PUBLIC)
# IMPORTANT : maintenant /films = recherche TMDB (plus SQLite)
# ============================================================
@app.get("/films")
def list_films(
    titre: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
):
    return tmdb_service.search_movies_min(query=titre, page=page, limit=limit)
"""


# ============================================================
# FAVORIS (AUTH REQUIRED via pseudo + password)
# Favori = film choisi dans TMDB (movie_id)
# ============================================================
@app.post(
    "/favorites/add_tmdb",
    response_model=FavoriteAddResponse,
    responses={401: {"model": ErrorResponse}},
)
def add_favorite_tmdb(
    pseudo: str = Query(...),
    password: str = Query(...),
    titre: str = Query(...),
):
    return user_client.add_favorite(pseudo, password, titre)

"""
@app.post(
    "/favorites/remove_tmdb",
    responses={401: {"model": ErrorResponse}},
)
def remove_favorite_tmdb(
    pseudo: Annotated[str, Form()],
    password: Annotated[str, Form()],
    movie_id: Annotated[int, Form()],
):
    user = authenticate_user(pseudo, password)
    if not user:
        return {"error": "Authentification échouée"}

    fav_service.remove_favorite(user_id=user["id_user"], movie_id=int(movie_id))
    return {"status": "ok"}
"""

@app.get("/favorites", responses={401: {"model": ErrorResponse}})
def get_favorites(pseudo: str, password: str):
    return user_client.get_favorites(pseudo, password)

'''
# ============================================================
# STATS (PUBLIC) - sur SQLite favorites + film
# ============================================================
@app.get("/stats/top_favorited")
def stats_top_favorited(limit: int = 10):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT f.id_film, f.titre, f.annee, f.realisateur, f.genre,
                   COUNT(*) AS nb_favoris
            FROM favorites fav
            JOIN film f ON f.id_film = fav.id_film
            GROUP BY f.id_film
            ORDER BY nb_favoris DESC
            LIMIT ?;
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []


# ============================================================
# ✅ NOUVEAU : Top films favoris par genre saisi par l'utilisateur
# ============================================================
@app.get("/stats/top_favorited_by_genre")
def stats_top_favorited_by_genre(
    genre: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Renvoie les films les plus ajoutés en favoris pour un genre donné.
    Comme film.genre est une chaîne type "Action, Drama", on filtre en LIKE (contains),
    insensible à la casse.
    """
    g = genre.strip().lower()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT f.id_film, f.titre, f.annee, f.realisateur, f.genre,
                   COUNT(*) AS nb_favoris
            FROM favorites fav
            JOIN film f ON f.id_film = fav.id_film
            WHERE LOWER(f.genre) LIKE ?
            GROUP BY f.id_film
            ORDER BY nb_favoris DESC
            LIMIT ?;
            """,
            (f"%{g}%", limit),
        )
        rows = cur.fetchall()

    return [dict(r) for r in rows] if rows else []
'''

if __name__ == "__main__":
    dao.drop_table()
    DAO()
    uvicorn.run(app, host="0.0.0.0", port=8000)
