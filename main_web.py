from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER

from dao.favorite_dao import FavoriteDao
from dao.film_dao import FilmDao
from dao.init_db import init_db
from service.auth_service import AuthService


init_db()

app = FastAPI(title="MovieReco Web")
app.add_middleware(SessionMiddleware, secret_key="CHANGE_ME_SECRET_KEY")

templates = Jinja2Templates(directory="templates")

auth = AuthService()
film_dao = FilmDao()
favorite_dao = FavoriteDao()


def current_user(request: Request):
    return request.session.get("user")


def require_login(request: Request):
    user = current_user(request)
    if not user:
        return None, RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return user, None


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user, redirect = require_login(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("home.html", {"request": request, "user": user})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
def login_action(request: Request, pseudo: str = Form(...), password: str = Form(...)):
    try:
        user = auth.login(pseudo=pseudo, password=password)
        request.session["user"] = user
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    except ValueError as e:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": str(e)}, status_code=400
        )


@app.post("/signup", response_class=HTMLResponse)
def signup_action(
    request: Request,
    pseudo: str = Form(...),
    password: str = Form(...),
    email: str | None = Form(default=None),
):
    try:
        auth.signup(pseudo=pseudo, password=password, email=email)
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    except ValueError as e:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": str(e)}, status_code=400
        )


@app.post("/logout")
def logout_post(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)


@app.get("/films", response_class=HTMLResponse)
def films_page(request: Request):
    user, redirect = require_login(request)
    if redirect:
        return redirect

    try:
        films = film_dao.get_all_films() or []
        fav_ids = favorite_dao.get_favorite_film_ids(user["id_user"]) or []
        fav_ids = set(fav_ids)

        return templates.TemplateResponse(
            "films.html",
            {"request": request, "user": user, "films": films, "fav_ids": fav_ids},
        )
    except Exception:
        import traceback

        return HTMLResponse(
            "<h1>Erreur /films</h1><pre>" + traceback.format_exc() + "</pre>",
            status_code=500,
        )


@app.get("/favorites", response_class=HTMLResponse)
def favorites_page(request: Request):
    user, redirect = require_login(request)
    if redirect:
        return redirect

    favorites = favorite_dao.list_favorites(user["id_user"])
    return templates.TemplateResponse(
        "favorites.html",
        {"request": request, "user": user, "favorites": favorites},
    )


@app.post("/favorites/add")
def add_favorite(request: Request, id_film: int = Form(...)):
    user, redirect = require_login(request)
    if redirect:
        return redirect

    favorite_dao.add_favorite(user["id_user"], id_film)
    return RedirectResponse(url="/films", status_code=HTTP_303_SEE_OTHER)


@app.post("/favorites/remove")
def remove_favorite(request: Request, id_film: int = Form(...)):
    user, redirect = require_login(request)
    if redirect:
        return redirect

    favorite_dao.remove_favorite(user["id_user"], id_film)
    return RedirectResponse(url="/films", status_code=HTTP_303_SEE_OTHER)
