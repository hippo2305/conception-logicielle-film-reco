from __future__ import annotations

import os
from typing import Annotated

from fastapi import FastAPI, Form, Query
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from starlette.status import HTTP_303_SEE_OTHER
import uvicorn

from dao.db_connection import get_connection
from dao.favorite_dao import FavoriteDao
from dao.film_dao import FilmDao
from dao.init_db import init_db
from service.auth_service import AuthService
from service.recommendation_service import RecommendationService


ROOT_PATH = os.getenv("ROOT_PATH", "/proxy/8000")  # "" en local si besoin

init_db()

app = FastAPI(root_path=ROOT_PATH, title="MovieReco API")

film_dao = FilmDao()
fav_dao = FavoriteDao()
reco_service = RecommendationService()
auth = AuthService()


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
# Models (pour nettoyer "Example Value" dans Swagger)
# ============================================================
class OkResponse(BaseModel):
    status: str = "ok"


class ErrorResponse(BaseModel):
    error: str


class SignupResponse(BaseModel):
    status: str = "ok"
    pseudo: str


class FavoriteResponse(BaseModel):
    status: str = "ok"
    titre: str


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs", status_code=HTTP_303_SEE_OTHER)


# ============================================================
# USERS
# ============================================================
@app.post(
    "/users/signup",
    response_model=SignupResponse,
    responses={400: {"model": ErrorResponse}},
)
def signup(
    pseudo: Annotated[str, Form()],
    password: Annotated[str, Form()],
    email: Annotated[str | None, Form()] = None,
):
    try:
        auth.signup(pseudo=pseudo, password=password, email=email)
        return {"status": "ok", "pseudo": pseudo}
    except ValueError as e:
        return {"error": str(e)}


def authenticate_user(pseudo: str, password: str):
    try:
        return auth.login(pseudo=pseudo, password=password)
    except ValueError:
        return None


# ============================================================
# FILMS (PUBLIC)
# ============================================================
@app.get("/films")
def list_films(
    titre: str | None = Query(default=None),
    genre: str | None = Query(default=None),
    limit: int = Query(default=100),
):
    return film_dao.search_films(q=titre, genre=genre, limit=limit)


# ============================================================
# FAVORIS (AUTH REQUIRED via pseudo + password)
# ============================================================


@app.post(
    "/favorites/add",
    response_model=FavoriteResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def add_favorite(
    pseudo: Annotated[str, Form()],
    password: Annotated[str, Form()],
    titre: Annotated[str, Form()],
    annee: Annotated[int | None, Form()] = None,
):
    # 1) Auth via pseudo+password (API garde pseudo)
    user = authenticate_user(pseudo, password)
    if not user:
        return {"error": "Authentification échouée"}

    # 2) Resolve titre(+annee) -> film_id (API garde titre)
    film = film_dao.get_film_by_title(titre, annee=annee)
    if not film:
        return {"error": f"Film introuvable: {titre}"}

    # 3) DAO attend (id_user, id_film)
    fav_dao.add_favorite(user_id=user["id_user"], film_id=film["id_film"])

    return {"status": "ok", "titre": film["titre"]}


@app.post(
    "/favorites/remove",
    response_model=FavoriteResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def remove_favorite(
    pseudo: Annotated[str, Form()],
    password: Annotated[str, Form()],
    titre: Annotated[str, Form()],
    annee: Annotated[int | None, Form()] = None,
):
    user = authenticate_user(pseudo, password)
    if not user:
        return {"error": "Authentification échouée"}

    film = film_dao.get_film_by_title(titre, annee=annee)
    if not film:
        return {"error": f"Film introuvable: {titre}"}

    fav_dao.remove_favorite(user_id=user["id_user"], film_id=film["id_film"])
    return {"status": "ok", "titre": film["titre"]}


@app.get("/favorites", responses={401: {"model": ErrorResponse}})
def list_favorites(pseudo: str, password: str):
    user = authenticate_user(pseudo, password)
    if not user:
        return {"error": "Authentification échouée"}

    # Ton DAO retourne déjà f.* (films)
    return fav_dao.list_favorites(user_id=user["id_user"])


# ============================================================
# RECOMMENDATIONS (PUBLIC)
# ============================================================
@app.get("/recommendations/by_genre")
def recommendations_by_genre(genre: str, limit: int = 10):
    return reco_service.recommend_by_genre(genre, limit=limit)


# ============================================================
# STATS (PUBLIC)
# ============================================================
@app.get("/stats/top_favorited")
def stats_top_favorited(limit: int = 10):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT f.titre, f.annee, COUNT(*) AS nb_favoris
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


@app.get("/stats/favorites_by_genre")
def stats_favorites_by_genre():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT f.genre, COUNT(*) AS nb_favoris
            FROM favorites fav
            JOIN film f ON f.id_film = fav.id_film
            GROUP BY f.genre
            ORDER BY nb_favoris DESC;
            """
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
