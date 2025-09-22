import asyncio
import logging

from dispytch.di.event import Event
from dispytch.di.context import EventHandlerContext
from dispytch.di.solver import solve_dependencies
from dispytch.listener.consumer import Consumer, Message
from dispytch.listener.handler import Handler
from dispytch.listener.handler_group import HandlerGroup
from dispytch.listener.handler_tree import HandlerTree
from dispytch.serialization import Deserializer
from dispytch.serialization.json import JSONDeserializer


class EventListener:
    """
    Coordinates the dispatch of consumed events to their corresponding handlers.

    Listens to an async event stream from the provided consumer and routes each event
    to the appropriate handler(s) based on topic and event type.

    Args:
        consumer (Consumer): The event source responsible for yielding incoming events.
        topic_delimiter (str): The symbol used to split topic names into segments for dynamic routing (default: ':').
    """

    def __init__(self, consumer: Consumer,
                 deserializer: Deserializer = None,
                 topic_delimiter: str = ':'):
        self.consumer = consumer
        self.deserializer = deserializer or JSONDeserializer()
        self.topic_delimiter: str = topic_delimiter
        self._tasks = set()
        self._handlers: HandlerTree = HandlerTree(topic_delimiter)

    async def listen(self):
        """
        Starts an async loop that consumes events and dispatches them to registered handlers.
        """

        async for message in self.consumer.listen():
            task = asyncio.create_task(self._handle_message(message))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

        if self._tasks:
            await asyncio.wait(self._tasks)

    async def _handle_message(self, msg: Message):
        event = Event(
            topic=msg.topic,
            **self.deserializer.deserialize(msg.payload).model_dump(),
        )

        handlers = self._handlers.get(event.topic, event.type)
        if not handlers:
            logging.info(f'There is no handler for topic `{event.topic}` and event type `{event.type}`')
            return

        tasks = [asyncio.create_task(
            self._call_handler_with_injected_dependencies(handler, event)
        ) for handler in handlers]
        await asyncio.gather(*tasks)

        await self.consumer.ack(msg)

    async def _call_handler_with_injected_dependencies(self, handler: Handler, event: Event):
        async with solve_dependencies(handler.func,
                                      EventHandlerContext(
                                          event=event,
                                          topic_pattern=handler.topic,
                                          topic_delimiter=self.topic_delimiter

                                      )) as deps:
            try:
                await handler.handle(**deps)
            except Exception as e:
                logging.exception(f"Handler {handler.func.__name__} failed for event {event.type}: {e}")

    def handler(self, *,
                topic: str,
                event: str,
                retries: int = 0,
                retry_on: type[Exception] = None,
                retry_interval: float = 1.25):
        """
            Decorator to register a handler function for a specific topic and event type.

            Args:
                topic (str): The topic this handler listens to.
                event (str): The event type this handler handles.
                retries (int, optional): Number of times to retry the handler on failure.
                    Defaults to 0 (no retries).
                retry_on (type[Exception], optional): Exception type to trigger retries.
                    If not set, retries will be attempted on any exception.
                retry_interval (float, optional): Delay in seconds between retries.
                    Defaults to 1.25 seconds.
            """

        def decorator(callback):
            self._handlers.insert(topic, event, Handler(callback, topic, retries, retry_interval, retry_on))
            return callback

        return decorator

    def add_handler_group(self, group: HandlerGroup):
        """
        Registers ``HandlerGroup``'s handlers with the listener.

        Args:
            group (HandlerGroup): A ``HandlerGroup`` object to register with the listener.
        """
        for topic in group.handlers:
            for event in group.handlers[topic]:
                self._handlers.insert(topic, event, *group.handlers[topic][event])
