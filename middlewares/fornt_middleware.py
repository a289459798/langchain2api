import typing
from typing import Any, Coroutine
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from fastapi import Request, Response
from starlette.types import ASGIApp

class ForntMiddleware(BaseHTTPMiddleware):
	def __init__(self, app: ASGIApp, dispatch: typing.Optional[DispatchFunction] = None) -> None:
		super().__init__(app, dispatch)

	async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Coroutine[Any, Any, Response]:
		headers = dict(request.scope['headers'])
		headers[b'uid'] = b'123'
		request.scope['headers'] = [(k, v) for k, v in headers.items()]
		response = await call_next(request)
		return response