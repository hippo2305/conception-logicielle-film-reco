from dao.dao import DAO


DAO()._drop_table()

DAO().add_database_from_csv("data/csv/films.csv", "FILMS")
print(DAO().query_data_base("FILMS", "*"))
