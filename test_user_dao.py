from src.client.film_client import FilmClient
from src.client.user_client import UserClient
from src.dao.dao import DAO


DAO().drop_table()

UserClient().signup("Hippo", "hippolytecotterot@gmail.com", "123Soleil!")
UserClient().add_favorite("Hippo", "123Soleil!", "Titanic")
favorites = UserClient().get_favorites("Hippo", "123Soleil!")
