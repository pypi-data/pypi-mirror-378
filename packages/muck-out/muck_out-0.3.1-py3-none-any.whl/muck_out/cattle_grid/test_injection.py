from fast_depends import inject

from cattle_grid.extensions.load import build_transformer
from cattle_grid.model import ActivityMessage

from muck_out.extension import extension
from muck_out.types import Activity

from . import ParsedActivity, ParsedActor


async def test_injection_activity():
    transformer = build_transformer([extension])
    actor_id = "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg"
    data = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "AnimalSound",
        "actor": actor_id,
        "to": ["https://www.w3.org/ns/activitystreams#Public"],
        "cc": ["http://abel/followers/RKsezXFc1SGvQKvucioJxg"],
        "published": "2025-09-17T18:34:00Z",
        "content": "meow",
        "id": "http://abel/simple_storage/019958f4-75e2-7039-b3fe-3538d3230d4f",
    }

    transformed = await transformer({"raw": data})

    def method(activity: ParsedActivity):
        assert isinstance(activity, Activity)
        assert activity.type == "AnimalSound"
        assert activity.content == "meow"

    injected_method = inject(method)
    message = ActivityMessage(actor=actor_id, data=transformed)
    injected_method(message=message)  # type: ignore


async def test_injection_actor_none():
    transformer = build_transformer([extension])
    actor_id = "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg"
    data = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "AnimalSound",
        "actor": actor_id,
        "to": ["https://www.w3.org/ns/activitystreams#Public"],
        "cc": ["http://abel/followers/RKsezXFc1SGvQKvucioJxg"],
        "published": "2025-09-17T18:34:00Z",
        "content": "meow",
        "id": "http://abel/simple_storage/019958f4-75e2-7039-b3fe-3538d3230d4f",
    }

    transformed = await transformer({"raw": data})

    def method(actor: ParsedActor):
        assert actor is None

    injected_method = inject(method)
    message = ActivityMessage(actor=actor_id, data=transformed)
    injected_method(message=message)  # type: ignore
