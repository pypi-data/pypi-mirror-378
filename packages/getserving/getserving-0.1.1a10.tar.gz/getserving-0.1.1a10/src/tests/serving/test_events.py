import asyncio
from pathlib import Path

import pytest
from bevy import get_container
from starlette.requests import Request
from starlette.responses import Response

from serving.auth import CredentialProvider
from serving.events import EventManager
from serving.serv import Serv
from serving.serv_middleware import ServMiddleware


class DummyCreds:
    def __init__(self, *, csrf_secret: str):
        self._secret = csrf_secret

    def has_credentials(self, permissions: set[str]) -> bool:
        return True

    def generate_csrf_token(self) -> str:
        return "token"

    def validate_csrf_token(self, token: str) -> bool:
        return True

    def create_session_token(self) -> str:
        return "session"

    def validate_session_token(self, token: str) -> bool:
        return True


_app_events: list[tuple[str, dict]] = []
_request_events: list[tuple[str, dict]] = []


async def record_app_event(*, label: str, **context):
    _app_events.append((label, context))


async def record_request_event(*, label: str, **context):
    _request_events.append((label, context))


@pytest.fixture(autouse=True)
def reset_events():
    _app_events.clear()
    _request_events.clear()
    yield
    _app_events.clear()
    _request_events.clear()


@pytest.mark.asyncio
async def test_app_level_events(tmp_path: Path):
    (tmp_path / "serving.dev.yaml").write_text(
        """
        environment: dev
        auth:
          credential_provider: tests.serving.test_events:DummyCreds
          config:
            csrf_secret: secret
        session:
          session_provider: serving.session:InMemorySessionProvider
        events:
          app.startup:
            - handler: tests.serving.test_events:record_app_event
              params:
                label: startup
          app.shutdown:
            - handler: tests.serving.test_events:record_app_event
              params:
                label: shutdown
          user.created:
            - tests.serving.test_events:record_app_event
        """
    )

    serv = Serv(working_directory=tmp_path, environment="dev")
    manager = serv.container.get(EventManager)

    await serv.app.router.startup()
    assert ("startup", {}) in _app_events

    await manager.trigger("user.created", label="created")
    assert ("created", {}) in _app_events

    await serv.app.router.shutdown()
    assert ("shutdown", {}) in _app_events


@pytest.mark.asyncio
async def test_request_event_manager_propagates(tmp_path: Path):
    (tmp_path / "serving.dev.yaml").write_text(
        """
        environment: dev
        auth:
          credential_provider: tests.serving.test_events:DummyCreds
          config:
            csrf_secret: secret
        session:
          session_provider: serving.session:InMemorySessionProvider
        events:
          request.start:
            - handler: tests.serving.test_events:record_app_event
              params:
                label: start-app
          request.finish:
            - handler: tests.serving.test_events:record_app_event
              params:
                label: finish-app
        """
    )

    serv = Serv(working_directory=tmp_path, environment="dev")
    middleware = ServMiddleware(app=None, serv=serv)

    scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    request = Request(scope)

    async def call_next(req):
        container = get_container()
        events = container.get(EventManager)
        events.register("request.finish", record_request_event, params={"label": "finish"})
        return Response("OK")

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    # finish events include both request and response
    assert ("start-app", {"request": request}) in _app_events
    finish_entry = next(item for item in _request_events if item[0] == "finish")
    assert finish_entry[1]["request"] is request
    assert isinstance(finish_entry[1]["response"], Response)

    app_finish = next(item for item in _app_events if item[0] == "finish-app")
    assert isinstance(app_finish[1]["request"], Request)
    assert isinstance(app_finish[1]["response"], Response)

    await serv.app.router.shutdown()
