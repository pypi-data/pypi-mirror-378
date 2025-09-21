from asyncio import CancelledError, get_running_loop
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from serving.response import ServResponse
from serving.events import EventManager

if TYPE_CHECKING:
    from serving.serv import Serv


class ServMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, serv: "Serv"):
        super().__init__(app)
        self.serv = serv

    async def dispatch(self, request, call_next):
        async with AsyncExitStack() as request_exit_stack:
            with self.serv.registry, self.serv.container.branch() as container:
                container.add(AsyncExitStack, request_exit_stack)
                events = self.serv.event_manager.child(container)
                container.add(EventManager, events)
                container.add(Request, request)
                container.add(
                    _response := ServResponse()
                )

                await events.trigger("request.start", request=request)

                response = None
                try:
                    _response.running_coroutine = get_running_loop().create_task(call_next(request))
                    try:
                        response = await _response.running_coroutine
                    except CancelledError:
                        if _response.response_override is None:
                            raise

                        response = _response.response_override
                    else:
                        if _response.response_override is not None:
                            response = _response.response_override

                    if response is not None:
                        response.headers.update(_response.headers)
                        if _response.status_code is not None:
                            response.status_code = _response.status_code

                    return response
                finally:
                    await events.trigger("request.finish", request=request, response=response)



