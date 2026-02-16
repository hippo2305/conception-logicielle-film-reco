from dao.dao import DAO


DAO()._del_data_table()

DAO().insert_query("ACTOR", "nom, prenom", "'Dicaprio', 'Leonardo'")
print(DAO().select_query("ACTOR"))
