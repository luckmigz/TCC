import aio_pika
import asyncio
import json
from typing import Callable, Awaitable

RABBITMQ_URL = "amqp://guest:guest@localhost/"

async def subscribe_to_queue(queue_name: str, callback: Callable[[dict], Awaitable[None]]):
    try:
        # Connect to RabbitMQ
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            print(f"Subscribed to queue: {queue_name}")
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            message_body = json.loads(message.body.decode('utf-8'))
                           
                            await callback(message_body)
                        except json.JSONDecodeError as e:
                            print(f"Failed to decode message: {e}")
                        except Exception as e:
                            print(f"Error processing message: {e}")

            print(f"Subscribed to {queue_name}. Waiting for messages...")
            await asyncio.Future()  
    except Exception as e:
        print(f"Failed to subscribe to queue {queue_name}: {e}")