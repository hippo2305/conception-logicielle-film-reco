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
from start import start


ROOT_PATH = os.getenv("ROOT_PATH", "/proxy/8000")  # "" en local si besoin
start()

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

@app.get("/favorites", responses={401: {"model": ErrorResponse}})
def get_favorites(pseudo: str, password: str):
    return user_client.get_favorites(pseudo, password)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
