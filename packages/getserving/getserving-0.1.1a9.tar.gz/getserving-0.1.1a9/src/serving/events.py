from __future__ import annotations

import importlib
import inspect
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cache
from typing import Any, Callable, Iterable, Mapping

from bevy import Container

Listener = Callable[..., Any]
DEFAULT_EVENT = "app.startup"


def _import_from_string(path: str) -> Listener:
    module_name, attr = path.split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


@dataclass
class HandlerSpec:
    handler: Listener | str
    params: dict[str, Any] = field(default_factory=dict)

    @cache
    def resolve(self) -> Listener:
        if isinstance(self.handler, str):
            self.handler = _import_from_string(self.handler)

        return self.handler

    def __hash__(self):
        return hash(self.handler)

    def __eq__(self, other):
        if not isinstance(other, HandlerSpec):
            return NotImplemented

        return self.handler == other.handler


class EventManager:
    """Registers and triggers application events.

    A manager lives in the application container and a child manager is injected
    into each request. Triggers flow from the active manager up to its parent so
    request events automatically reach application listeners.
    """

    def __init__(
        self,
        container: Container,
        *,
        parent: "EventManager | None" = None,
        handlers: dict[str, Iterable[HandlerSpec]] | None = None,
    ):
        self._container = container
        self._parent = parent
        self._handlers: dict[str, list[HandlerSpec]] = defaultdict(list)
        if handlers:
            for event, specs in handlers.items():
                for spec in specs:
                    self._handlers[event].append(spec)

    def register(self, event: str, handler: Listener | HandlerSpec | str, *, params: dict[str, Any] | None = None) -> None:
        """Register a handler for an event."""
        self._handlers[event].append(
            handler if isinstance(handler, HandlerSpec) else HandlerSpec(handler, params or {})
        )

    async def trigger(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Trigger an event and propagate to the parent manager."""
        for spec in self._handlers.get(event, []):
            func = spec.resolve()
            call_kwargs = {**spec.params, **kwargs}
            result = self._container.call(func, *args, **call_kwargs)
            if inspect.isawaitable(result):
                await result

        if self._parent is not None:
            await self._parent.trigger(event, *args, **kwargs)

    def child(self, container: Container) -> "EventManager":
        """Create a child manager bound to a descendant container."""
        return EventManager(container, parent=self)

    @classmethod
    def from_config(cls, container: Container, config: Mapping[str, Iterable[Any]]) -> "EventManager":
        return cls(
            container,
            handlers=cls.parse_config(config),
        )

    @staticmethod
    def parse_config(config: Mapping[str, Iterable[Any]] | None) -> dict[str, list[HandlerSpec]]:
        handlers: dict[str, list[HandlerSpec]] = defaultdict(list)
        if not config:
            return handlers

        for event, entries in config.items():
            if isinstance(entries, str):
                handlers[event].append(HandlerSpec(entries, {}))
                continue

            if not isinstance(entries, Iterable):
                raise ValueError("Event handlers for each key must be an iterable or string")

            for entry in entries:
                if isinstance(entry, str):
                    handlers[event].append(HandlerSpec(entry, {}))
                    continue

                if not isinstance(entry, dict) or "handler" not in entry:
                    raise ValueError("Event configuration dictionaries must include a 'handler'")

                params = entry.get("params", {}) or {}
                if not isinstance(params, dict):
                    raise ValueError("Event handler 'params' must be a mapping")

                handlers[event].append(HandlerSpec(entry["handler"], params))

        return handlers


__all__ = ["EventManager", "HandlerSpec", "DEFAULT_EVENT"]
