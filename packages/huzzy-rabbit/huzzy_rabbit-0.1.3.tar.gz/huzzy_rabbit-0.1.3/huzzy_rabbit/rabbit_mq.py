import asyncio
import json
import logging
from typing import Callable, Optional

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError, ChannelClosed


class RabbitMQ:
    exchanges = {}
    channel: Optional[AbstractChannel] = None
    connection: Optional[AbstractRobustConnection] = None
    connection_url: Optional[str] = None
    is_connecting = False
    reconnect_interval = 5  # seconds
    logger = logging.getLogger(__name__)

    @staticmethod
    async def connect(connection_url: str, max_retries: int = 3) -> None:
        """Initialize connection with retry logic"""
        RabbitMQ.connection_url = connection_url
        retries = 0
        while retries < max_retries:
            try:
                await RabbitMQ._connect()
                return
            except AMQPConnectionError as e:
                retries += 1
                RabbitMQ.logger.error(
                    f"Connection attempt {retries}/{max_retries} failed: {str(e)}"
                )
                if retries == max_retries:
                    raise Exception("Max connection retries reached")
                await asyncio.sleep(RabbitMQ.reconnect_interval)

    @staticmethod
    async def _connect() -> None:
        """Internal connection method"""
        if RabbitMQ.is_connecting:
            return
        try:
            RabbitMQ.is_connecting = True
            RabbitMQ.connection = await connect_robust(
                RabbitMQ.connection_url, reconnect_interval=RabbitMQ.reconnect_interval
            )
            RabbitMQ.channel = await RabbitMQ.connection.channel()
            await RabbitMQ.channel.set_qos(prefetch_count=1)
            # Re-declare exchanges after reconnection
            for exchange_name in list(RabbitMQ.exchanges.keys()):
                await RabbitMQ.declare_exchange(exchange_name)
        finally:
            RabbitMQ.is_connecting = False

    @staticmethod
    async def ensure_connection() -> None:
        """Ensure connection is active, reconnect if needed"""
        if not RabbitMQ.connection or RabbitMQ.connection.is_closed:
            await RabbitMQ._connect()
        elif not RabbitMQ.channel or RabbitMQ.channel.is_closed:
            RabbitMQ.channel = await RabbitMQ.connection.channel()
            await RabbitMQ.channel.set_qos(prefetch_count=1)
            
            
    @staticmethod
    async def publish(
        message_dict: dict,
        exchange_name: str,
        routing_key: str,
        message: Message = None,
        routing_action: str = None,
    ) -> None:
        """Publish message with connection handling"""
        await RabbitMQ.ensure_connection()

        if message is None:
            message_body = json.dumps(message_dict).encode()
            message = Message(
                message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
            )

        try:
            exchange: AbstractExchange = RabbitMQ.exchanges[exchange_name]
        except KeyError:
            raise Exception(f"Exchange {exchange_name} not found")

        message.headers = {"action": routing_action} if routing_action else {}

        try:
            await exchange.publish(message, routing_key=routing_key)
        except (ChannelClosed, AMQPConnectionError):
            RabbitMQ.logger.warning(
                "Channel closed during publish, attempting reconnect"
            )
            await RabbitMQ.ensure_connection()
            exchange = RabbitMQ.exchanges[exchange_name]
            await exchange.publish(message, routing_key=routing_key)

    @staticmethod
    async def declare_exchange(exchange_name: str) -> AbstractExchange:
        """Declare exchange with connection handling"""
        await RabbitMQ.ensure_connection()

        exchange = await RabbitMQ.channel.declare_exchange(
            exchange_name,
            type=ExchangeType.DIRECT,
            durable=True,
        )
        RabbitMQ.exchanges[exchange_name] = exchange
        return exchange

    @staticmethod
    async def declare_queue_and_bind(
        queue_name: str,
        exchange_name: str,
        app_listener: Callable,
        routing_key: str = None,
    ) -> None:
        """Declare queue and bind with connection handling"""
        await RabbitMQ.ensure_connection()

        queue = await RabbitMQ.channel.declare_queue(queue_name, durable=True)

        try:
            exchange: AbstractExchange = RabbitMQ.exchanges[exchange_name]
        except KeyError:
            raise Exception(f"Exchange {exchange_name} not found")

        routing_key = routing_key if routing_key else queue_name

        # Binding the queue to the exchange
        await queue.bind(exchange, routing_key)
        await queue.consume(app_listener)

    @staticmethod
    async def declare_queue(
        queue_name: str, exchange_name: str, routing_key: str = None
    ) -> None:
        """Declare queue with connection handling"""
        await RabbitMQ.ensure_connection()

        queue = await RabbitMQ.channel.declare_queue(queue_name, durable=True)

        try:
            exchange: AbstractExchange = RabbitMQ.exchanges[exchange_name]
        except KeyError:
            raise Exception(f"Exchange {exchange_name} not found")

        routing_key = routing_key if routing_key else queue_name
        await queue.bind(exchange, routing_key)

    @staticmethod
    async def remote_procedure_call(
        queue_name: str, on_response: Callable, correlation_id: str, message_dict: dict
    ) -> None:
        """Handle RPC with connection handling"""
        await RabbitMQ.ensure_connection()

        message_body = json.dumps(message_dict).encode()
        queue = await RabbitMQ.channel.declare_queue(queue_name, durable=True)
        message = Message(
            message_body,
            delivery_mode=DeliveryMode.PERSISTENT,
            correlation_id=correlation_id,
            reply_to=queue.name,
        )

        try:
            await RabbitMQ.publish(
                message=message,
                routing_key="rpc_queue",
                exchange_name="rpc_exchange",
                message_dict=message_dict,
            )
            await queue.consume(on_response, no_ack=True)
        except (ChannelClosed, AMQPConnectionError):
            RabbitMQ.logger.warning("Connection lost during RPC, attempting reconnect")
            await RabbitMQ.ensure_connection()
            queue = await RabbitMQ.channel.declare_queue(queue_name, durable=True)
            await RabbitMQ.publish(
                message=message,
                routing_key="rpc_queue",
                exchange_name="rpc_exchange",
                message_dict=message_dict,
            )
            await queue.consume(on_response, no_ack=True)

    @staticmethod
    async def close() -> None:
        """Clean up connection"""
        if RabbitMQ.channel and not RabbitMQ.channel.is_closed:
            await RabbitMQ.channel.close()
        if RabbitMQ.connection and not RabbitMQ.connection.is_closed:
            await RabbitMQ.connection.close()
