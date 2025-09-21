from contextlib import AsyncExitStack

import pytest
from bevy import get_container
from bevy.registries import Registry
from starlette.requests import Request
from starlette.responses import Response

from serving.serv_middleware import ServMiddleware
from serving.events import EventManager


class _DummyServ:
    def __init__(self, registry: Registry, container):
        self.registry = registry
        self.container = container
        self.event_manager = EventManager(container)


@pytest.mark.asyncio
async def test_request_branch_has_exit_stack():
    registry = Registry()
    parent_container = registry.create_container()
    serv = _DummyServ(registry, parent_container)
    middleware = ServMiddleware(app=None, serv=serv)

    scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    request = Request(scope)

    cleanup_called = False

    async def call_next(req):
        nonlocal cleanup_called
        container = get_container()
        stack = container.get(AsyncExitStack)

        async def marker():
            nonlocal cleanup_called
            cleanup_called = True

        stack.push_async_callback(marker)
        return Response("OK")

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert cleanup_called is True
