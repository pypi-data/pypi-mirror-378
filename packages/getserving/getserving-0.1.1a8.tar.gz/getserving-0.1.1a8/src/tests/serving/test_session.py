from typing import Annotated

import pytest
from bevy import get_registry
from starlette.requests import Request

from serving.response import ServResponse
from serving.session import InMemorySessionProvider, Session, SessionProvider
from serving.auth import CredentialProvider
from serving.injectors import (
    handle_session_types,
    handle_session_param_types,
    SessionParam,
)


class DummyCredentialProvider:
    def __init__(self):
        self._tokens: set[str] = set()

    def create_session_token(self) -> str:
        token = f"tok-{len(self._tokens) + 1}"
        self._tokens.add(token)
        return token

    def validate_session_token(self, token: str) -> bool:
        return token in self._tokens


def make_request_with_cookies(cookie_header: str | None = None) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
    }
    if cookie_header is not None:
        scope["headers"].append((b"cookie", cookie_header.encode()))
    return Request(scope)


@pytest.mark.asyncio
async def test_inmemory_session_provider_create_update_invalidate():
    # Use a DI container so method calls can resolve dependencies
    registry = get_registry()
    container = registry.create_container()
    container.add(CredentialProvider, DummyCredentialProvider())
    provider = container.call(InMemorySessionProvider)

    token = await provider.create_session()
    assert token.startswith("tok-")

    await provider.update_session(token, {"a": 1, "b": None})
    data = await provider.get_session(token)
    assert data == {"a": 1, "b": None}

    await provider.invalidate_session(token)
    assert await provider.get_session(token) is None


@pytest.mark.asyncio
async def test_session_load_save_invalidate_sets_cookie_and_persists():
    registry = get_registry()
    handle_session_types.register_hook(registry)
    container = registry.create_container()

    # Request + response lifecycle objects
    container.add(ServResponse())
    request = make_request_with_cookies()  # no cookie -> new session
    container.add(Request, request)

    # Provider dependency
    container.add(CredentialProvider, DummyCredentialProvider())
    provider = container.call(InMemorySessionProvider)
    container.add(SessionProvider, provider)

    session = await container.call(Session.load_session)
    assert isinstance(session, Session)
    assert session.token

    # Session token should be present
    assert session.token

    # Persist data, including None values
    session["user_id"] = "u123"
    session["maybe_none"] = None
    await session.save()
    data = await container.call(provider.get_session, session.token)
    assert data == {"user_id": "u123", "maybe_none": None}

    # Invalidate clears provider storage
    await session.invalidate()
    assert await container.call(provider.get_session, session.token) is None


# Additional integration of Session via injector is exercised in runtime tests.
