import asyncio
import functools
import json
import logging

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.adapters.blocking_connection import BlockingConnection
from pika.exchange_type import ExchangeType

from src.api import config

# def get_rabbitmq_connection():
#     print("Connecting to RabbitMQ..." , RABBITMQ_URL)
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL))
#     channel = connection.channel()
#     channel.queue_declare(queue=QUEUE_NAME, durable=True)
#
#     return connection, channel


log = logging.getLogger(__name__)

# class RabbitMQConnection(object):
#     def __init__(self, url= config.RABBITMQ_URL,
#                  exchange=config.RABBITMQ_EXCHANGE,
#                  exchange_type=ExchangeType.direct,
#                  queue=config.RABBITMQ_QUEUE,
#                  routing_key=config.RABBITMQ_ROUTING_KEY):
#         # self._connection = connect(url, loop=asyncio.get_running_loop())
#         self._connection = None
#         self._channel = None
#
#         self._url = url
#
#         self.EXCHANGE = exchange
#         self.EXCHANGE_TYPE = exchange_type
#         self.QUEUE = queue
#         self.ROUTING_KEY = routing_key
#
#
#     async def connect(self):
#         log.info('Connecting to %s', self._url)
#         self._connection = await connect(self._url, loop=asyncio.get_running_loop())
#         self._channel = await self._connection.channel()
#         await self._channel.declare_exchange(self.EXCHANGE, self.EXCHANGE_TYPE, durable=True)

class AsyncioRabbitMQ(object):
    _connection : AsyncioConnection= None
    _channel = None

    def __init__(self, url= config.RABBITMQ_URL,
                 exchange=config.RABBITMQ_EXCHANGE,
                 exchange_type=ExchangeType.direct,
                 queue=config.RABBITMQ_QUEUE,
                 routing_key=config.RABBITMQ_ROUTING_KEY):
        self._message_number = 0

        self._url = url

        self.EXCHANGE = exchange
        self.EXCHANGE_TYPE = exchange_type
        self.QUEUE = queue
        self.ROUTING_KEY = routing_key

        self.connect()

    def connect(self) -> AsyncioConnection:
        log.info('Connecting to %s', self._url)
        return AsyncioConnection(
            pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )

    def on_connection_open(self, connection):
        log.info('Connection opened')
        self._connection = connection
        log.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_open_error(self, _unused_connection, err):
        log.error('Connection open failed: %s', err)

    def on_connection_closed(self, _unused_connection, reason):
        log.warning('Connection closed: %s', reason)
        self._channel = None

    def on_channel_open(self, channel):
        log.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        log.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        log.warning('Channel %i was closed: %s', channel, reason)
        self._channel = None
        self._connection.close()

    def setup_exchange(self, exchange_name):
        log.info('Declaring exchange %s', exchange_name)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(exchange=exchange_name, exchange_type=self.EXCHANGE_TYPE, callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        log.info('Exchange declared: %s', userdata)
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        log.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(queue=queue_name, callback=self.on_queue_declareok)

    def on_queue_declareok(self, _unused_frame):
        log.info('Binding %s to %s with %s', self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        self._channel.queue_bind(self.QUEUE, self.EXCHANGE, routing_key=self.ROUTING_KEY, callback=self.on_bindok)

    def on_bindok(self, _unused_frame):
        log.info('Queue bound')

    async def publish_message(self, message : dict):
        if self._channel is None or not self._channel.is_open:
            return

        properties = pika.BasicProperties(
            app_id='api-server',
            content_type='application/json',
            delivery_mode=2
        )

        self._channel.basic_publish(self.EXCHANGE, self.ROUTING_KEY,
                                    json.dumps(message, ensure_ascii=False),
                                    properties)
        self._message_number += 1
        log.info('Published message # %i', self._message_number)


# rabbitMQClient = AsyncioRabbitMQ(config.RABBITMQ_URL)
