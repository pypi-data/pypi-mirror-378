from asyncio import TimeoutError
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from aio_pika import Message
from aio_pika.abc import AbstractExchange, DeliveryMode
from pydantic import BaseModel

from dispytch.emitter.producer import Producer, ProducerTimeout


class RabbitMQEventConfig(BaseModel):
    exchange: str | None = None
    delivery_mode: DeliveryMode | int | None = None
    priority: int | None = None
    expiration: int | datetime | float | timedelta | None = None
    headers: dict[str, bool | bytes | Decimal | list | dict[
        str, Any] | float | int | None | str | datetime] | None = None
    content_type: str | None = None
    content_encoding: str | None = None
    correlation_id: str | None = None
    reply_to: str | None = None
    message_id: str | None = None
    timestamp: int | datetime | float | timedelta | None = None
    type: str | None = None
    user_id: str | None = None
    app_id: str | None = None


class RabbitMQProducer(Producer):
    def __init__(self,
                 exchanges: list[AbstractExchange],
                 timeout: int | float | None = None) -> None:
        self.exchanges = {exchange.name: exchange for exchange in exchanges}
        self.timeout = timeout

    async def send(self, topic: str, payload: bytes, config: BaseModel | None = None):
        if config is not None and not isinstance(config, RabbitMQEventConfig):
            raise ValueError(
                f"Expected a RabbitMQEventConfig when using RabbitMQProducer got {type(config).__name__}"
            )
        config = config or RabbitMQEventConfig()

        try:
            await self.exchanges[config.exchange or next(iter(self.exchanges))].publish(
                Message(
                    body=payload,
                    delivery_mode=config.delivery_mode,
                    priority=config.priority,
                    expiration=config.expiration,
                    headers=config.headers,
                    content_type=config.content_type,
                    content_encoding=config.content_encoding,
                    correlation_id=config.correlation_id,
                    reply_to=config.reply_to,
                    message_id=config.message_id,
                    timestamp=config.timestamp,
                    type=config.type,
                    user_id=config.user_id,
                    app_id=config.app_id,
                ),
                routing_key=topic,
                timeout=self.timeout,
            )
        except TimeoutError:
            raise ProducerTimeout()
