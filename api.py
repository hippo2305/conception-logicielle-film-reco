from __future__ import annotations

import hashlib
import secrets
from typing import Annotated

from fastapi import FastAPI, Form, Query
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
import uvicorn

from dao.db_connection import get_connection
from dao.favorite_dao import FavoriteDao
from dao.film_dao import FilmDao
from dao.init_db import init_db
from dao.user_dao import UserDao
from service.recommendation_service import RecommendationService


ROOT_PATH = "/proxy/8000"


# -----------------------
# Password helpers
# -----------------------
def hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return dk.hex()


def make_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"pbkdf2${salt}${hash_password(password, salt)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt, h = stored.split("$", 2)
        if algo != "pbkdf2":
            return False
        return hash_password(password, salt) == h
    except Exception:
        return False


# -----------------------
# Init app
# -----------------------
init_db()

app = FastAPI(root_path=ROOT_PATH, title="MovieReco API (pseudo + password)")

film_dao = FilmDao()
fav_dao = FavoriteDao()
user_dao = UserDao()
reco_service = RecommendationService()


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs", status_code=HTTP_303_SEE_OTHER)


# ============================================================
# USERS
# ============================================================
@app.post("/users/signup")
def signup(
    pseudo: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    if not pseudo:
        return {"error": "Pseudo vide"}
    if len(password) < 4:
        return {"error": "Mot de passe trop court"}

    if user_dao.get_user_row_by_pseudo(pseudo):
        return {"error": "Pseudo déjà utilisé"}

    password_hash = make_password_hash(password)

    ok = user_dao.create_minimal(
        pseudo=pseudo,
        password_hash=password_hash,
        email=None,
        role="client",
        listfilms="[]",
    )

    if not ok:
        return {"error": "Impossible de créer l'utilisateur"}

    return {"status": "ok", "pseudo": pseudo}


def authenticate_user(pseudo: str, password: str):
    user = user_dao.get_user_row_by_pseudo(pseudo)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


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
@app.post("/favorites/add")
def add_favorite(
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

    fav_dao.add_favorite(user["id_user"], film["id_film"])
    return {"status": "ok", "titre": film["titre"]}


@app.post("/favorites/remove")
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

    fav_dao.remove_favorite(user["id_user"], film["id_film"])
    return {"status": "ok", "titre": film["titre"]}


@app.get("/favorites")
def list_favorites(
    pseudo: str,
    password: str,
):
    user = authenticate_user(pseudo, password)
    if not user:
        return {"error": "Authentification échouée"}

    return fav_dao.list_favorites(user["id_user"])


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


# ============================================================
# RECOMMENDATIONS (PUBLIC)
# ============================================================
@app.get("/recommendations/by_title")
def recommendations_by_title(titre: str, limit: int = 10):
    return reco_service.recommend_by_title(titre, limit=limit)


@app.get("/recommendations/by_genre")
def recommendations_by_genre(genre: str, limit: int = 10):
    return reco_service.recommend_by_genre(genre, limit=limit)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
