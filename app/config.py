import logging

from dotenv import load_dotenv
from os import getenv


load_dotenv()


class Settings:
    API_KEY_FILES_SERVICE: str = getenv('API_KEY_FILES_SERVICE')
    URL_FILES_SERVICE: str = getenv('URL_FILES_SERVICE')
    URL_RABBIT_MQ: str = getenv('URL_RABBIT_MQ')
    RECAPTCHA_KEY: str = getenv('RECAPTCHA_KEY')
    ENVIRONMENT: str = getenv('ENVIRONMENT')
    MONGO_URL: str = getenv('MONGO_URL')
    DB_NAME: str = getenv('DB_NAME')
    PORT: str = getenv('PORT')

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

settings = Settings()
