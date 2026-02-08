from business_object.actor import Actor
from business_object.film import Film
from dao.film_dao import FilmDAO


actor1 = Actor("Vivien", "Leigh")
actor2 = Actor("Clark", "Gable")
actor3 = Actor("Olivia", "de Havilland")

film = Film("Gone with the Wind", "Victor Fleming", "drame", [actor1, actor2, actor3])
print(film)

FilmDAO()._drop_table()

FilmDAO().add_film(film)

#FilmDAO().get_all_films()
