from src.client.user_client import UserClient
from src.dao.dao import DAO


def start():
    DAO().drop_table()

    UserClient().signup("jean_mich", "jean-michel@gmail.com", "123Soleil!")
    UserClient().signup("francis", "francis@gmail.com", "Alsoe:Poslkj!9547")
    UserClient().signup("xX_darkenzo_Xx", "darkenzo@skyrock.fr", "1L0v3G@m3s")

    UserClient().add_favorite("jean_mich", "123Soleil!", "Titanic")
    UserClient().add_favorite("jean_mich", "123Soleil!", "Star Wars")
    UserClient().add_favorite("jean_mich", "123Soleil!", "Inception")

    UserClient().add_favorite("francis", "Alsoe:Poslkj!9547", "Gone with the Wind")
    UserClient().add_favorite("francis", "Alsoe:Poslkj!9547", "The Sound of Music")
    UserClient().add_favorite("francis", "Alsoe:Poslkj!9547", "Doctor Zhivago")

    UserClient().add_favorite("xX_darkenzo_Xx", "1L0v3G@m3s", "Avatar")
    UserClient().add_favorite("xX_darkenzo_Xx", "1L0v3G@m3s", "Avengers: Endgame")
    UserClient().add_favorite("xX_darkenzo_Xx", "1L0v3G@m3s", "Titanic")
