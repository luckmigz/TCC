import aio_pika
import asyncio
import json
import logging
from typing import Callable, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_URL = "amqp://rabbitmq-service:5672"
_channel: Optional[aio_pika.abc.AbstractChannel] = None

async def get_connection() -> aio_pika.abc.AbstractChannel:
    global _channel
    if not _channel or _channel.is_closed:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        _channel = await connection.channel()
    return _channel

async def subscribe_to_event(queue_name: str, callback: Callable[[dict], None]) -> None:
    """
    Escuta mensagens de uma fila e executa um callback.
    """
    try:
        channel = await get_connection()
        queue = await channel.declare_queue(queue_name, durable=False)

        logger.info(f" [*] Waiting for messages in {queue_name}. To exit press CTRL+C")

        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body_str = message.body.decode('utf-8')
                    msg = json.loads(body_str)
                    logger.info(f" [x] Received {body_str}")
                    callback(msg)
                    # ack automático via message.process()
                except Exception as e:
                    logger.error("Erro ao processar mensagem", exc_info=e)

        await queue.consume(on_message, no_ack=False)

    except Exception as e:
        logger.error("Erro ao consumir mensagens da fila", exc_info=e)

async def purge_queue(queue_name: str) -> None:
    """
    Limpa todas as mensagens pendentes da fila.
    """
    try:
        channel = await get_connection()
        await channel.queue_purge(queue_name)
        logger.info(f"Fila '{queue_name}' limpa com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao limpar fila '{queue_name}'", exc_info=e)
