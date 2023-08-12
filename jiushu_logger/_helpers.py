# coding: utf-8
import typing

import orjson

__all__ = ['ENV_HEADERS', 'safely_jsonify']

ENV_HEADERS = (
    'X-Varnish',
    'X-Request-Start',
    'X-Heroku-Queue-Depth',
    'X-Real-Ip',
    'X-Forwarded-Proto',
    'X-Forwarded-Protocol',
    'X-Forwarded-Ssl',
    'X-Heroku-Queue-Wait-Time',
    'X-Forwarded-For',
    'X-Heroku-Dynos-In-Use',
    'X-Forwarded-Protocol',
    'X-Forwarded-Port',
    'X-Request-Id',
    'Via',
    'Total-Route-Time',
    'Connect-Time'
)


def safely_jsonify(obj: typing.Any) -> str:
    """Jsonify object safely."""
    try:
        return orjson.dumps(obj).decode('utf_8', errors='ignore')

    except:
        return str(obj)
