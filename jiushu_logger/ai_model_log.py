# coding: utf-8
from http import HTTPStatus
from time import time
from typing import Any

import httpx

from .helpers import safely_jsonify

__all__ = ['AiModelLogSdk']


class AiModelLogSdk:
    """AI model log SDK"""

    def __init__(self, url: str):
        """
        Constructor.
        :param url: Endpoint of the logging API.
        """
        self.__url = url

    def send(self,
             trace_id: str,
             name: str,
             version: str,
             param: Any,
             result: Any,
             duration: float,
             status: int = 0,
             error_msg: str = "",
             ) -> bool:
        """
        Send log message.

        :param trace_id: Trace ID.
        :param name: Name of model.
        :param version: Version of model.
        :param param: Input parameters of model.
        :param result: Output results of model.
        :param duration: In second. Duration of model inference.
        :param status: 0 for success, else for failure.
        :param error_msg: Message to display in case of failure.
        :return: True for success, False for failure.
        """

        try:
            resp = httpx.post(self.__url,
                              json={
                                  'traceId': trace_id,
                                  'name': name,
                                  'version': version,
                                  'param': safely_jsonify(param),
                                  'result': safely_jsonify(result),
                                  'status': status,
                                  'errorMsg': error_msg,
                                  'time': int(duration * 1000),
                                  'busTime': int(time() * 1000)
                              },
                              timeout=httpx.Timeout(5.))
            return resp.status_code == HTTPStatus.OK

        except BaseException as e:
            return False
