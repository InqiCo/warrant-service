import logging

from dotenv import load_dotenv
from os import getenv


load_dotenv()


class Settings:
    URL_RABBIT_MQ: str = getenv('URL_RABBIT_MQ')
    RECAPTCHA_KEY: str = getenv('RECAPTCHA_KEY')
    MONGO_URL: str = getenv('MONGO_URL')
    DB_NAME: str = getenv('DB_NAME')

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

settings = Settings()
