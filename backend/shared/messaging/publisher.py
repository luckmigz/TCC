import aio_pika
import asyncio
import logging

# Configura logging (opcional, como console.log)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_URL = "amqp://rabbitmq-service:5672"

async def publish_event(queue: str, msg: str):
    """
    Envia uma mensagem string para uma fila não-durável no RabbitMQ,
    exatamente como o código JS faz.
    """
    try:
        # Conexão com RabbitMQ
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        # Declarar fila (não-durável, como no JS)
        await channel.declare_queue(queue, durable=False)

        # Enviar mensagem como string simples
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=msg.encode(),
                delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT  # igual ao JS
            ),
            routing_key=queue
        )

        logger.info(f"[x] Sent {msg}")

        # Espera 1 segundo antes de fechar (como o setTimeout do JS)
        await asyncio.sleep(1)
        await connection.close()

    except Exception as e:
        logger.error("Erro ao enviar mensagem para a fila", exc_info=e)

# Exemplo de uso (equivalente ao "main")
async def main():
    await publish_event("minha_fila", "Mensagem de teste")

if __name__ == "__main__":
    asyncio.run(main())
