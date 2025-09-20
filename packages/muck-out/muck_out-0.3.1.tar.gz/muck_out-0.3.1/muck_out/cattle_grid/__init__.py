from collections.abc import Awaitable, Callable
from typing import Annotated
from fast_depends import Depends

from muck_out.types import Activity, Actor, Object, Collection

from .fetch import (
    fetch_activity_builder,
    fetch_actor_builder,
    fetch_collection_builder,
    fetch_object_builder,
)

from .methods import (
    get_activity,
    get_actor,
    get_collection,
    get_embedded_object,
    get_object,
)


ParsedActivity = Annotated[Activity | None, Depends(get_activity)]
"""Returns the parsed activity from the muck_out extension.

This dependency works for methods that would normally receive
a [ActivityMessage][cattle_grid.model.ActivityMessage], e.g.
the `incoming.*` and `outgoing.*` subscriber of cattle_grid.
"""

ParsedActor = Annotated[Actor | None, Depends(get_actor)]
"""Returns the parsed actor from the muck_out extension.

This dependency works for methods that would normally receive
a [ActivityMessage][cattle_grid.model.ActivityMessage], e.g.
the `incoming.*` and `outgoing.*` subscriber of cattle_grid.
"""

ParsedCollection = Annotated[Collection | None, Depends(get_collection)]
"""Returns the parsed collection from the muck_out extension.

This dependency works for methods that would normally receive
a [ActivityMessage][cattle_grid.model.ActivityMessage], e.g.
the `incoming.*` and `outgoing.*` subscriber of cattle_grid.
"""

ParsedEmbeddedObject = Annotated[Object | None, Depends(get_embedded_object)]
"""Returns the parsed embededed object from an activity from the muck_out extension.

This dependency works for methods that would normally receive
a [ActivityMessage][cattle_grid.model.ActivityMessage], e.g.
the `incoming.*` and `outgoing.*` subscriber of cattle_grid.
"""

ParsedObject = Annotated[Object | None, Depends(get_object)]
"""Returns the parsed object from the muck_out extension.

This dependency works for methods that would normally receive
a [ActivityMessage][cattle_grid.model.ActivityMessage], e.g.
the `incoming.*` and `outgoing.*` subscriber of cattle_grid.
"""

FetchActivity = Annotated[
    Callable[[str, str], Awaitable[Activity | None]], Depends(fetch_activity_builder)
]
"""Returns the actovoty after fetching it"""
FetchActor = Annotated[
    Callable[[str, str], Awaitable[Actor | None]], Depends(fetch_actor_builder)
]
"""Returns the actor after fetching it"""
FetchCollection = Annotated[
    Callable[[str, str], Awaitable[Collection | None]],
    Depends(fetch_collection_builder),
]
"""Returns the collection after fetching it"""
FetchObject = Annotated[
    Callable[[str, str], Awaitable[Object | None]], Depends(fetch_object_builder)
]
"""Returns the object after fetching it"""
