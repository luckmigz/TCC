import aio_pika
import asyncio
import json 

RABBITMQ_URL = "amqp://guest:guest@localhost/"  
async def publish_message(queue_name: str,  message: dict):
    try:
        # Connect to RabbitMQ
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            
            channel = await connection.channel()
            await channel.declare_queue(queue_name, durable=True)

       
            message_body = json.dumps(message).encode('utf-8')
            await channel.default_exchange.publish(
                aio_pika.Message(body=message_body),
                routing_key=queue_name
            )
            print(f"Message published to {queue_name} ")
            await connection.close()
    except Exception as e:
        print(f"Failed to publish message: {e}")