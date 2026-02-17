from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse

from src.service.tmdb_service import TmdbService


app = FastAPI(root_path="/proxy/5000", title="FuelTrack API")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.get("/tmdb/search")
async def tmdb_search_movie(q: str = Query(..., min_length=1), page: int = 1):
    return await TmdbService().search_movie(query=q, page=page)


@app.get("/tmdb/movie/{movie_id}")
async def tmdb_movie_details(movie_id: int):
    return await TmdbService().movie_details(movie_id=movie_id)
