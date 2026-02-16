from dao.dao import DAO
from dao.film_dao import FilmDAO
from service.actor_service import ActorService
from service.film_service import FilmService


DAO()._drop_table()

actor1 = ActorService().instantiate_actor("Hamill", "Mark")

actor2 = ActorService().instantiate_actor("Ford", "Harrison")

actor3 = ActorService().instantiate_actor("Fisher", "Carrie")

actor4 = ActorService().instantiate_actor("Guiness", "Alec")

actor5 = ActorService().instantiate_actor("Prowse", "David")

actor6 = ActorService().instantiate_actor("Driver", "Adam")

actor7 = ActorService().instantiate_actor("Ridley", "Daisy")

film1 = FilmService().instantiate_film(
    "Star Wars IV: A New Hope",
    "George Lucas",
    1977,
    "science-fiction",
)

FilmService().add_casting(film1, [actor1, actor2, actor3, actor4, actor5])

FilmService().save_film(film1)

film2 = FilmService().instantiate_film(
    "Star Wars VII: The Force Awakens",
    "J.J. Abrams",
    2015,
    "science-fiction",
)

FilmService().add_casting(film2, [actor2, actor1, actor3, actor6, actor7])

FilmService().save_film(film2)

print(f"Films avec {actor1.prenom} {actor1.nom}")
films = ActorService().get_films(actor1)
for film in films:
    FilmService().add_casting(film, FilmDAO().get_casting(film))
    print(film)

actors1 = FilmDAO().get_casting(films[0])

print("")
print(f"Acteurs de {films[0].titre}")
for actor in actors1:
    print(actor)

actors2 = FilmDAO().get_casting(films[1])

print("")
print(f"Acteurs de {films[1].titre}")
for actor in actors2:
    print(actor)
