# coding: utf-8
import typing

import orjson

__all__ = ['safely_jsonify']


def safely_jsonify(obj: typing.Any) -> str:
    """Jsonify object safely."""
    try:
        return orjson.dumps(obj).decode('utf_8', errors='ignore')

    except:
        return str(obj)
