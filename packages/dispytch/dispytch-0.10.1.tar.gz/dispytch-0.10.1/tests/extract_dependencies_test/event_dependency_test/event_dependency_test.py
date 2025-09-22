import uuid

import pytest
from pydantic import BaseModel, ValidationError

from dispytch.di.context import EventHandlerContext
from dispytch.di.event import Event
from dispytch.di.extractor import extract_dependencies
from dispytch.di.dependency import Dependency


@pytest.fixture
def event_dict():
    return Event(**{
        'id': str(uuid.uuid4()),
        'topic': 'test-topic',
        'type': 'test-type',
        'body': {
            'name': 'test',
            'value': 42
        },
        'timestamp': 100
    })


@pytest.fixture
def event_dict_with_empty_body():
    return Event(**{
        'id': str(uuid.uuid4()),
        'topic': 'test-topic',
        'type': 'test-type',
        'body': {},
        'timestamp': 100
    })


@pytest.fixture
def event_dict_with_additional_data():
    return Event(**{
        'id': str(uuid.uuid4()),
        'topic': 'test-topic',
        'type': 'test-type',
        'body': {
            'name': 'test',
            'value': 42,
            'additional': 'extra data',
            'timestamp': '2023-01-01T00:00:00Z'
        },
        'timestamp': 100
    })


class EventBody(BaseModel):
    name: str
    value: int


class EventBodyWithOptional(BaseModel):
    name: str
    value: int = 0
    optional: str = None


class OnlyNameNeededModel(BaseModel):
    name: str


class OnlyValueNeededModel(BaseModel):
    value: int


def assert_dict_was_interpreted(received_event: Event, initial_event: Event):
    assert received_event.topic == initial_event.topic
    assert received_event.type == initial_event.type
    assert received_event.body.name == initial_event.body['name']
    assert received_event.body.value == initial_event.body['value']


@pytest.mark.asyncio
async def test_event_dependency(event_dict):
    def func_with_event(event_param: Event[EventBody]):
        pass

    result = extract_dependencies(func_with_event)

    assert len(result) == 1

    dep = result["event_param"]
    assert isinstance(dep, Dependency)

    async with dep(ctx=EventHandlerContext(event=event_dict, topic_pattern="topic", topic_delimiter=':')) as event:
        assert isinstance(event, Event)
        assert isinstance(event.body, EventBody)
        assert_dict_was_interpreted(event, event_dict)


@pytest.mark.asyncio
async def test_multiple_event_dependencies(event_dict):
    def func_with_multiple_events(
            e1: Event[EventBody],
            e2: Event[EventBodyWithOptional]
    ):
        pass

    result = extract_dependencies(func_with_multiple_events)

    assert len(result) == 2
    assert "e1" in result
    assert "e2" in result

    async with result["e1"](ctx=EventHandlerContext(event=event_dict,
                                                    topic_pattern="topic",
                                                    topic_delimiter=':')) as event1:
        assert isinstance(event1, Event)
        assert isinstance(event1.body, EventBody)
        assert_dict_was_interpreted(event1, event_dict)

    async with result["e2"](ctx=EventHandlerContext(event=event_dict,
                                                    topic_pattern="topic",
                                                    topic_delimiter=':')) as event2:
        assert isinstance(event2, Event)
        assert isinstance(event2.body, EventBodyWithOptional)
        assert_dict_was_interpreted(event2, event_dict)
        assert event2.body.optional is None


@pytest.mark.asyncio
async def test_multiple_event_dependencies_with_different_fields_of_event_needed(event_dict):
    def func_with_multiple_events(
            e1: Event[OnlyNameNeededModel],
            e2: Event[OnlyValueNeededModel]
    ):
        pass

    result = extract_dependencies(func_with_multiple_events)

    assert len(result) == 2
    assert "e1" in result
    assert "e2" in result

    async with result["e1"](ctx=EventHandlerContext(event=event_dict,
                                                    topic_pattern="topic",
                                                    topic_delimiter=':')) as event1:
        assert isinstance(event1, Event)
        assert isinstance(event1.body, OnlyNameNeededModel)
        assert event1.body.name == event_dict.body['name']

        with pytest.raises(AttributeError):
            assert event1.body.value

    async with result["e2"](ctx=EventHandlerContext(event=event_dict,
                                                    topic_pattern="topic",
                                                    topic_delimiter=':')) as event2:
        assert isinstance(event2, Event)
        assert isinstance(event2.body, OnlyValueNeededModel)
        assert event2.body.value == event_dict.body['value']

        with pytest.raises(AttributeError):
            assert event2.body.name


@pytest.mark.asyncio
async def test_empty_event_body(event_dict_with_empty_body):
    def func_with_event(event_param: Event[EventBody]):
        pass

    result = extract_dependencies(func_with_event)

    with pytest.raises(ValidationError):
        async with result["event_param"](
                ctx=EventHandlerContext(event=event_dict_with_empty_body,
                                        topic_pattern="topic",
                                        topic_delimiter=':')):
            pass


@pytest.mark.asyncio
async def test_additional_event_data_ignored(event_dict_with_additional_data):
    def func_with_event(event_param: Event[EventBody]):
        pass

    result = extract_dependencies(func_with_event)

    async with result["event_param"](
            ctx=EventHandlerContext(event=event_dict_with_additional_data,
                                    topic_pattern="topic",
                                    topic_delimiter=':')) as event:
        assert isinstance(event, Event)
        assert isinstance(event.body, EventBody)
        assert_dict_was_interpreted(event, event_dict_with_additional_data)

        with pytest.raises(AttributeError):
            assert event.body.additional == 'extra data'

        with pytest.raises(AttributeError):
            assert event.body.timestamp == '2023-01-01T00:00:00Z'


@pytest.mark.asyncio
async def test_getting_all_event_data_as_dict(event_dict_with_additional_data):
    def func_with_event(event_param: Event):
        pass

    result = extract_dependencies(func_with_event)

    async with result["event_param"](
            ctx=EventHandlerContext(event=event_dict_with_additional_data,
                                    topic_pattern="topic",
                                    topic_delimiter=':')) as event:
        assert isinstance(event, Event)
        assert isinstance(event.body, dict)

        assert event.body == event_dict_with_additional_data.body
