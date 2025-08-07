from typing import Any, Dict
import base64

from pymongo import ReturnDocument
import requests

from app.config import logger, settings
from app.db import get_brazil_datetime, collection_queries, collection_compliance, collection_lawsuits, \
    collection_services_pricing, collection_companies, generate_index, collection_history_credits


def decode_base64_if_needed(data_str: str):
    """
    Valida se a string é base64 (mesmo que com data URI) e retorna o conteúdo decodificado,
    ou None se não for base64 válido.
    """
    try:
        if data_str.startswith('data:'):
            data_str = data_str.split(',', 1)[1]
        return base64.b64decode(data_str, validate=True)
    except Exception as e:
        logger.error(f'Error decode_base64_if_needed {e}')
        return None


def upload_file_to_service(file_data: str, query_id: str, service_code: str) -> str:
    """
    Faz o upload de um arquivo (base64 ou HTML) para o serviço de arquivos.

    Args:
        file_data (str): O conteúdo do arquivo, possivelmente codificado em base64.
        query_id (str): ID da consulta, usado na composição do nome do arquivo.
        service_code (str): Código do serviço que está fazendo o upload.
        settings: Objeto com as configurações (URL, API Key, ambiente, etc).

    Returns:
        str: Caminho completo do arquivo enviado com extensão.
    """
    url = f'{settings.URL_FILES_SERVICE}/upload'
    data_now = str(get_brazil_datetime())

    is_base64 = decode_base64_if_needed(file_data) is not None
    ext = 'pdf' if is_base64 else 'html'

    full_filename = f'InqiCo/{settings.ENVIRONMENT}/{service_code}/{query_id}/{data_now}'

    payload = {
        'data': file_data,
        'filename': full_filename
    }

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': settings.API_KEY_FILES_SERVICE
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    return f'{full_filename}.{ext}'


async def save_result(query_id: str, result_data: Dict[str, Any], body: Dict[str, Any]):
    now = get_brazil_datetime()

    service_category_map = {
        'warrants': 'compliance',
        'criminal-record': 'compliance',
        'social-benefits': 'compliance',
        'lawsuits': 'lawsuits'
    }

    if result_data.get('file'):
        result_data['file'] = upload_file_to_service(
            file_data=result_data['file'],
            query_id=query_id,
            service_code=body['service_code']
        )

    category = service_category_map[body['service_code']]
    storage_collection = {
        'compliance': collection_compliance,
        'lawsuits': collection_lawsuits
    }.get(category)

    await storage_collection.update_one(
        {'query_id': query_id},
        {'$set': {
            body['service_code']: result_data,
            'updated_at': now
        }}
    )

    await collection_queries.update_one(
        {'_id': query_id},
        {'$set': {
            f'status.{body["service_code"]}': 'PS',
            'updated_at': now
        }}
    )

    logger.info(f'[SAVE_RESULT] Resultado de {body["service_code"]} salvo para query {query_id}')

    query_doc = await collection_queries.find_one({'_id': query_id})
    company_id = query_doc.get('company_id')

    service_doc = await collection_services_pricing.find_one({'service_code': body["service_code"]})
    credit_cost = service_doc.get('credit_cost', 0)

    await collection_companies.find_one_and_update(
        filter={'_id': company_id, 'credits': {'$gte': credit_cost}},
        update={'$inc': {'credits': -credit_cost}},
        return_document=ReturnDocument.AFTER
    )

    data_save_history = {
        'service_code': body['service_code'],
        'user_id': query_doc['user_id'],
        'credit_cost': credit_cost,
        'query_id': query_id,
        'company_id': company_id,
    }
    base_index = generate_index()
    base_index.update(data_save_history)

    await collection_history_credits.insert_one(base_index)

    return (f'[CREDITOS] {credit_cost} crédito(s) consumido(s) da empresa {company_id} p'
            f'ara o serviço {body["service_code"]}')
