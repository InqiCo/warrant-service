from datetime import datetime

import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

collection_queries = db['queries']


def get_brazil_datetime():
    timezone = pytz.timezone('America/Sao_Paulo')
    return datetime.now(timezone).replace(tzinfo=None)
