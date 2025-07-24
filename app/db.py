from datetime import datetime
import uuid
import pytz

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

collection_authentications_logs= db['authentications_logs']
collection_services_pricing = db['services_pricing']
collection_history_credits = db['history_credits']
collection_compliance = db['compliance']
collection_inquilinos = db['inquilinos']
collection_schedules = db['schedules']
collection_companies = db['companies']
collection_lawsuits = db['lawsuits']
collection_queries = db['queries']
collection_users = db['users']


def get_brazil_datetime():
    timezone = pytz.timezone('America/Sao_Paulo')
    return datetime.now(timezone).replace(tzinfo=None)


def generate_index():
    base_insert = {
        '_id': str(uuid.uuid4()),
        'is_active': True,
        'is_deleted': False,
        'created_at': get_brazil_datetime(),
        'updated_at': get_brazil_datetime()
    }

    return base_insert
