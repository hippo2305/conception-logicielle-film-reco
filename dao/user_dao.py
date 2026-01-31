from dao import DAO


class UserDAO(DAO):
    def get_all_users(self):
        return self.query_csv_file("data/csv/user.csv","*")


if __name__ == "__main__":
    print(UserDAO().get_all_users())