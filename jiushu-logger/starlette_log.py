# coding: utf-8
# Try to import starlette to find whether it was installed
try:
    import starlette
except:
    starlette = NotImplemented

if starlette is NotImplemented:
    __all__ = []

else:
    import typing
    from time import perf_counter
    from uuid import uuid1
    import re
    import orjson
    from itertools import chain
    from _helpers import *

    from log import Logger, ReqLogExtra
    from starlette.applications import Starlette
    from starlette.concurrency import iterate_in_threadpool
    from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import Response

    __all__ = ['RouterLoggingMiddleware']


    def _get_headers(request: Request):
        headers = dict(request.headers)
        for key in ENV_HEADERS:
            if key in headers:
                del headers[key]
        return headers


    class _AsyncIteratorWrapper:
        """The following is a utility class that transforms a
                regular iterable to an asynchronous one."""

        def __init__(self, obj):
            self._it = iter(obj)

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                value = next(self._it)
            except StopIteration:
                raise StopAsyncIteration
            return value


    class RouterLoggingMiddleware(BaseHTTPMiddleware):
        def __init__(self,
                     app: Starlette,
                     *,
                     skip_routes: typing.Sequence[str] = None,
                     skip_regexes: typing.Sequence[str] = None):
            self._skip_routes = skip_routes or []
            self._skip_regexes = (
                [re.compile(regex) for regex in skip_regexes]
                if skip_regexes
                else [])

            super().__init__(app)

        def __should_route_be_skipped(self, request_route: str) -> bool:
            return any(chain(
                iter(True for route in self._skip_routes if request_route.startswith(route)),
                iter(True for regex in self._skip_regexes if regex.match(request_route)),
            ))

        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
            trace_id = uuid1().hex
            request.state.trace_id = trace_id

            start_time = perf_counter()
            response = await call_next(request)
            duration = perf_counter() - start_time

            # https://github.com/encode/starlette/issues/495
            resp_body = [section async for section in response.__dict__['body_iterator']]
            response.__setattr__('body_iterator', iterate_in_threadpool(iter(resp_body)))

            # request body
            data = await request.body()
            form = dict(await request.form())
            try:
                json_ = orjson.loads(data)
            except:
                json_ = None

            if json_ is None:
                if form:
                    body = form
                else:
                    body = data
            else:
                body = json_

            # response body
            resp = b''.join(resp_body)
            try:
                resp = orjson.loads(resp)
            except:
                pass

            if not self.__should_route_be_skipped(request.url.path):
                Logger.req.info(
                    None,
                    extra=ReqLogExtra(
                        trace_id=trace_id,
                        duration=duration,
                        method=request.method,
                        path=request.url.path,
                        client_ip=next(iter(request.headers.getlist('X-Forwarded-For')), request.client.host),
                        host=request.url.hostname,
                        headers=safely_jsonify(_get_headers(request)),
                        query=safely_jsonify(dict(request.query_params)),
                        body=safely_jsonify(body),
                        resp=safely_jsonify(resp)))

            response.headers['X-Request-Id'] = trace_id
            return response
