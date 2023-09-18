# coding: utf-8
import typing

import orjson

__all__ = ['safely_jsonify']


def safely_jsonify(obj: typing.Any, truncate: typing.Optional[int] = None) -> str:
    """Jsonify object safely."""
    try:
        result = orjson.dumps(obj).decode('utf_8', errors='ignore')
    except:
        result = str(obj)
    if truncate is not None and truncate > 0:
        result = result[:truncate]
    return result
