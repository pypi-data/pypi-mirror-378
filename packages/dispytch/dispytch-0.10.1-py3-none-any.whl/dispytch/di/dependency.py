import inspect
from collections.abc import Callable
from contextlib import asynccontextmanager
from inspect import isawaitable
from typing import Any, AsyncContextManager, AsyncGenerator, AsyncIterator, Generator, Iterator, ContextManager

from dispytch.di.exc import InvalidGeneratorError
from dispytch.di.context import EventHandlerContext


def _get_async_cm_from_iterator(gen: AsyncIterator | Iterator):
    @asynccontextmanager
    async def wrapper():
        try:
            yield await gen.__anext__() if hasattr(gen, "__anext__") else next(gen)
        except (StopAsyncIteration, StopIteration):
            raise InvalidGeneratorError("Generator didn't yield any value")

        try:
            await gen.__anext__() if hasattr(gen, "__anext__") else next(gen)
        except (StopAsyncIteration, StopIteration):
            pass
        else:
            raise InvalidGeneratorError("Generator yielded more than one value")

    return wrapper()


def _get_async_cm_from_cm(sync_cm: ContextManager[Any]):
    @asynccontextmanager
    async def wrapper():
        with sync_cm as value:
            yield value

    return wrapper()


DependencyType = Callable[
    ..., Any | AsyncContextManager | ContextManager | AsyncGenerator | Generator | AsyncIterator | Iterator]


class Dependency:
    """Wraps a dependency provider for injection.

    This container is used to define functions, generators, or async context managers
    as injectable dependencies within the framework.

    Args:
        func: A callable, generator, or context manager that provides the dependency.
        use_cache:
            If True (default), the result will be cached and reused across injections.
            If False, the dependency will be freshly resolved every time, and no caching will occur.
    """

    def __init__(self, func: DependencyType, *, use_cache=True):
        self.func = func
        self.use_cache = use_cache

    def _get_context_param_name(self) -> str | None:
        sig = inspect.signature(self.func)
        for name, param in sig.parameters.items():
            if param.annotation is EventHandlerContext:
                return name
        return None

    def __call__(self, *, ctx: EventHandlerContext = None, **kwargs) -> AsyncContextManager[Any]:
        if ctx_param_name := self._get_context_param_name():
            kwargs[ctx_param_name] = ctx

        res = self.func(**kwargs)

        if isinstance(res, AsyncContextManager):
            return res

        if isinstance(res, ContextManager):
            return _get_async_cm_from_cm(res)

        if isinstance(res, (AsyncIterator, Iterator)):
            return _get_async_cm_from_iterator(res)

        @asynccontextmanager
        async def wrapper():
            if isawaitable(res):
                value = await res
            else:
                value = res
            yield value

        return wrapper()

    def __hash__(self):
        return hash(self.func)
