import os

from dotenv import load_dotenv


class MAIN:
    @staticmethod
    def load_env() -> None:
        load_dotenv()
        if os.path.exists(".env"):
            load_dotenv(".env", override=True)
