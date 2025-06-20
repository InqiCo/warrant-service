import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
import asyncio
import json

from aio_pika import connect_robust, Message

from app.db import collection_queries, get_brazil_datetime
from service.run_crawler import CrawlerCriminal
from app.config import settings, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await connect_robust(settings.URL_RABBIT_MQ)
    channel = await connection.channel()

    queue = await channel.declare_queue(f'publish-warrants-{settings.ENVIRONMENT}', durable=True)

    async def consume(queue, name_queue):
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        raw = message.body.decode()
                        body = json.loads(raw)

                        logger.info(f'[{name_queue}] Mensagem recebida: {body['query_id']}')

                        await collection_queries.update_one(
                            {'_id': body['query_id']},
                            {
                                '$set': {
                                    f'status.{body['service_code']}': 'IP',
                                    'updated_at': get_brazil_datetime()
                                }
                            }
                        )

                        crawler = CrawlerCriminal('portalbnmp.cnj.jus.br')
                        result = crawler.search(body)

                        logger.info(f'[{name_queue}] Mensagem processada com sucesso.')

                        body.update({'result': result})
                        new_message_body = json.dumps(body)

                        await channel.default_exchange.publish(
                            Message(new_message_body.encode()),
                            routing_key=f'result-warrants-{settings.ENVIRONMENT}'
                        )

                    except Exception as e:
                        logger.error(f'[{name_queue}] Erro ao processar mensagem: {e}')
                        raise

    tasks = [
        asyncio.create_task(consume(queue, f'publish-warrants-{i+1}'))
        for i in range(3)
    ]

    yield

    for task in tasks:
        task.cancel()

    await connection.close()


app = FastAPI(lifespan=lifespan)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0', port=int(settings.PORT),
        reload=True
    )
