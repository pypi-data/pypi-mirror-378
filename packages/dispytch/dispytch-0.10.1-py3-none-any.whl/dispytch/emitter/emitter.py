import logging
import time
from inspect import isawaitable
from typing import Callable

from dispytch.emitter.event import EventBase
from dispytch.emitter.producer import Producer, ProducerTimeout
from dispytch.serialization import Serializer
from dispytch.serialization.json import JSONSerializer

logger = logging.getLogger(__name__)


class EventEmitter:
    """
    Used for sending events using the provided producer.

    Wraps a low-level producer and emits structured EventBase instances
    to the appropriate topic with metadata and payload.

    Args:
        producer (Producer): The message producer responsible for sending events.
    """

    def __init__(self, producer: Producer, serializer: Serializer = None) -> None:
        self.producer = producer
        self.serializer = serializer or JSONSerializer()
        self._on_timeout = lambda e: logger.warning(f"Event {e} hit a timeout during emission")

    async def emit(self, event: EventBase):
        try:
            await self.producer.send(
                topic=_get_formatted_topic(event),
                payload=self.serializer.serialize({
                    'id': event.id,
                    'type': event.__event_type__,
                    'body': event.model_dump(mode="json", by_alias=True, exclude={'id'}),
                    'timestamp': int(time.time() * 1000),
                }),
                config=event.__backend_config__
            )
        except ProducerTimeout:
            if isawaitable(res := self._on_timeout(event)):
                await res

    def on_timeout(self, callback: Callable[[EventBase], None]):
        self._on_timeout = callback
        return callback


def _get_formatted_topic(event: EventBase) -> str:
    try:
        return event.__topic__.format(**event.model_dump())
    except KeyError as e:
        raise RuntimeError(
            f"Missing an event field `{e.args[0]}` "
            f"used to form a topic name `{event.__topic__}`"
            f" on event {event.__class__.__name__}") from e
    except IndexError:
        raise RuntimeError(
            f"Malformed topic name `{event.__topic__}`. Use an event field name in {{}} "
        )
