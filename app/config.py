from dotenv import load_dotenv
from os import getenv


load_dotenv()


class Settings:
    URL_RABBIT_MQ: str = getenv('URL_RABBIT_MQ')
    RECAPTCHA_KEY: str = getenv('RECAPTCHA_KEY')
    MONGO_URL: str = getenv('MONGO_URL')
    DB_NAME: str = getenv('DB_NAME')

settings = Settings()
