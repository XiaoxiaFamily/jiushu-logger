# coding: utf-8
import re
import typing
from itertools import chain
from time import perf_counter
from uuid import uuid1

import orjson

from _helpers import *
from log import Logger, ReqLogExtra

try:
    import flask
except:
    flask = NotImplemented

if flask is NotImplemented:
    __all__ = []

else:
    __all__ = ['RouterLogging']


    def _get_headers():
        headers = dict(flask.request.headers.items())
        for key in ENV_HEADERS:
            if key in headers:
                del headers[key]
        return headers


    class RouterLogging:
        def __init__(self,
                     app: flask.Flask,
                     *,
                     skip_routes: typing.Sequence[str] = None,
                     skip_regexes: typing.Sequence[str] = None):
            self._skip_routes = skip_routes or []
            self._skip_regexes = (
                [re.compile(regex) for regex in skip_regexes]
                if skip_regexes
                else [])
            app.before_request(self._before_request_func)
            app.after_request(self._after_request_func)

        def __should_route_be_skipped(self, request_route: str) -> bool:
            return any(chain(
                iter(True for route in self._skip_routes if request_route.startswith(route)),
                iter(True for regex in self._skip_regexes if regex.match(request_route)),
            ))

        def _before_request_func(self):
            flask.g.trace_id = uuid1().hex
            flask.g.begin_time = perf_counter()

        def _after_request_func(self, response: flask.Response):
            # DO NOT output logs for the route which should be skipped
            if self.__should_route_be_skipped(flask.request.path):
                pass

            else:
                # request body
                data = flask.request.data
                form = flask.request.form.to_dict()
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
                try:
                    resp = orjson.loads(response.get_data())
                except:
                    resp = response.get_data()

                Logger.req.info(
                    '',
                    extra=ReqLogExtra(
                        trace_id=flask.g.trace_id,
                        duration=perf_counter() - flask.g.begin_time,
                        method=flask.request.method,
                        path=flask.request.path,
                        client_ip=flask.request.headers.get('X-Forwarded-For', flask.request.remote_addr),
                        host=flask.request.host,
                        headers=safely_jsonify(_get_headers()),
                        query=safely_jsonify(flask.request.args.to_dict()),
                        body=safely_jsonify(body),
                        resp=safely_jsonify(resp)
                    )
                )

            response.headers.setdefault('X-Request-Id', flask.g.trace_id)
            return response
