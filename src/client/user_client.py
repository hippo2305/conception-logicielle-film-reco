from src.business_object.user import User
from src.service.user_service import UserService


class UserClient:
    def __init__(self):
        self.user_service = UserService()

    def signup(self, pseudo, email, password):
        user = User(pseudo=pseudo, email=email, passwd=password)
        self.user_service.signup(user)

    def login(self, pseudo, password):
        return self.user_service.login(pseudo, password)
