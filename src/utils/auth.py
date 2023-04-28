import time
import pika
import threading
from utils.watch import logger


class RabbitMQConnection:
    def __init__(self):
        self.credentials = pika.PlainCredentials('worker', 'work4a11ies')
        self.parameters = pika.ConnectionParameters(
            '192.168.1.29', credentials=self.credentials,
            virtual_host='gova11y')
        self.connection = None
        self.connect()

    def connect(self):
        logger.debug('Connecting to RabbitMQ server...')
        self.connection = pika.BlockingConnection(self.parameters)
        logger.debug('Connected to RabbitMQ server!')

    def close(self):
        self.connection.close()

    def get_channel(self):
        return self.connection.channel()


rabbitmq_connection = RabbitMQConnection()


def rabbit(queue_name, message):
    logger.debug('Running Rabbit')
    channel = rabbitmq_connection.get_channel()

    logger.debug(f'Declaring queue: {queue_name}...')
    channel.queue_declare(
        queue=queue_name, durable=True, arguments={'x-message-ttl': 7200000})
    logger.debug(f'Queue {queue_name} declared!')

    try:
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2)  # Make the messages persistent
        )
        channel.close()
        return channel
    except Exception as e:
        logger.error(f"You've got a sick rabbit... {e}")
        return None
        time.sleep(15)


def catch_rabbits(queue_name, callback):
    logger.debug('Running catch_rabbits')
    channel = rabbitmq_connection.get_channel()

    logger.debug(f'Declaring queue: {queue_name}...')
    channel.queue_declare(
        queue=queue_name, durable=True, arguments={'x-message-ttl': 7200000})
    logger.debug(f'Queue {queue_name} declared!')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False
    )
    logger.info(
        f'🐇 [*] Waiting for messages in {queue_name}. To exit press CTRL+C')

    # Create a separate thread to start consuming messages from the queue
    consumer_thread = threading.Thread(target=channel.start_consuming)
    consumer_thread.start()