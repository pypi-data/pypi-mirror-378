from functools import lru_cache
from typing import Annotated

from dispytch import EventEmitter
from dispytch.rabbitmq import RabbitMQProducer
from fastapi import Depends as FastAPIDependency, Request


@lru_cache  # emitter doesn't need to change throughout the application lifetime, so I made it singleton
def emitter(request: Request):
    return EventEmitter(
        RabbitMQProducer(
            exchange=request.app.state.rabbitmq.post_exchange,  # this service will send events to post events exchange
        )
    )


EmitterDep = Annotated[EventEmitter, FastAPIDependency(emitter)]
