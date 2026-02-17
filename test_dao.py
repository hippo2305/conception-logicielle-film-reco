from src.business_object.actor import Actor
from src.dao.actor_dao import ActorDAO
from src.dao.dao import DAO


DAO()._drop_table()

test_actor1 = Actor("Dicaprio", "Leonardo")
test_actor2 = Actor("Cruise", "Tom")

ActorDAO().add_actor(test_actor1)
ActorDAO().add_actor(test_actor2)

print(ActorDAO().get_all_actors()[1])
