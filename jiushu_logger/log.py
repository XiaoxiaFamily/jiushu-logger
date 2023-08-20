# coding: utf-8
import logging
import sys
import typing
from dataclasses import dataclass, fields
from enum import Enum

from ._helpers import safely_jsonify

__all__ = ['Logger', 'BizLogExtra', 'ReqLogExtra', 'CallLogExtra',
           'CronLogExtra', 'MiddlewareLogExtra', 'MqLogExtra',
           'CallType', 'MiddlewareType', 'MqType', 'MqHandleType']

# Change warning level name from WARNING to WARN
logging.addLevelName(logging.WARNING, 'WARN')

# Base log format
_base_format = ('level: [%(levelname)s], '
                'cate: [%(cate)s], '
                'traceId: [%(trace_id)s], '
                'timestamp: [%(created)d%(msecs)03d], '
                'duration: [%(duration)s], '
                'runtime: [{"file": "%(filename)s", '
                '"codeLine": "%(lineno)d", '
                '"func": "%(funcName)s", '
                '"threadId": "%(threadName)s-%(thread)d"}], ')
# BIZ log format
_biz_format = _base_format + 'msg: [%(message)s]'
# REQ log format
_req_format = _base_format + ('method: [%(method)s], '
                              'path: [%(path)s], '
                              'clientIp: [%(client_ip)s], '
                              'host: [%(host)s], '
                              'headers: [%(headers)s], '
                              'query: [%(query)s], '
                              'body: [%(body)s], '
                              'resp: [%(resp)s], '
                              'msg: [%(message)s]')
# CALL log format
_call_format = _base_format + 'callParams: [%(call_params)s], callResp: [%(call_resp)s], msg: [%(message)s]'
# CRON log format
_cron_format = _base_format + 'jobGroup: [%(job_group)s], jobCode: [%(job_code)s], msg: [%(message)s]'
# MIDDLEWARE log format
_middleware_format = _base_format + 'host: [%(host)s], msg: [%(message)s]'
# MQ log format
_mq_format = _base_format + 'handle: [%(handle)s], msg: [%(message)s]'


def _init_logger(cate: str, fmt: str):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.NOTSET)
    handler.setFormatter(logging.Formatter(fmt, datefmt='%Y-%m-%d,%H:%M:%S'))
    logger = logging.getLogger(f'jf_service_{cate}')
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


@dataclass(init=False, repr=False, eq=False, frozen=True)
class Logger:
    biz: typing.ClassVar = _init_logger('biz', _biz_format)
    req: typing.ClassVar = _init_logger('req', _req_format)
    call: typing.ClassVar = _init_logger('call', _call_format)
    cron: typing.ClassVar = _init_logger('cron', _cron_format)
    middleware: typing.ClassVar = _init_logger('middleware', _middleware_format)
    mq: typing.ClassVar = _init_logger('mq', _mq_format)


# ----- 业务日志 -----
@dataclass
class BizLogExtra(typing.Mapping):
    cate: str = 'biz'
    trace_id: str = None
    duration: typing.Union[int, float] = None

    def __post_init__(self):
        assert self.cate == 'biz'
        if self.duration is not None:
            self.duration = int(self.duration * 1000)  # s -> ms

    def __getitem__(self, field_name):
        return getattr(self, field_name)

    def __len__(self) -> int:
        return len(fields(self))

    def __iter__(self):
        yield from (field.name for field in fields(self))


@dataclass
class ReqLogExtra(BizLogExtra):
    cate: str = 'req'
    method: str = None
    path: str = None
    client_ip: str = None
    host: str = None
    headers: str = None
    query: str = None
    body: str = None
    resp: str = None

    def __post_init__(self):
        assert self.cate == 'req'
        if self.duration is not None:
            self.duration = int(self.duration * 1000)  # s -> ms


class CallType(Enum):
    INTERN = 'internalCall'
    EXTERN = 'externalCall'

    def __repr__(self):
        return self.value


@dataclass
class CallLogExtra(BizLogExtra):
    cate: typing.Union[str, CallType] = None
    call_params: typing.Union[str, typing.Mapping] = None
    call_resp: typing.Union[str, typing.Mapping] = None

    def __post_init__(self):
        assert self.cate and self.cate in CallType
        self.cate = str(self.cate)
        if self.call_params is not None:
            self.call_params = safely_jsonify(self.call_params)
        if self.call_resp is not None:
            self.call_resp = safely_jsonify(self.call_resp)
        if self.duration is not None:
            self.duration = int(self.duration * 1000)  # s -> ms


@dataclass
class CronLogExtra(BizLogExtra):
    cate: str = 'cron'
    job_group: str = None
    job_code: str = None

    def __post_init__(self):
        assert self.cate == 'cron'
        if self.duration is not None:
            self.duration = int(self.duration * 1000)  # s -> ms


class MiddlewareType(Enum):
    MYSQL = 'mysql'
    MONGO = 'mongo'
    REDIS = 'redis'
    ES = 'es'

    def __repr__(self):
        return self.value


@dataclass
class MiddlewareLogExtra(BizLogExtra):
    cate: typing.Union[str, MiddlewareType] = None
    host: str = None

    def __post_init__(self):
        assert self.cate and self.cate in MiddlewareType
        self.cate = str(self.cate)
        if self.duration is not None:
            self.duration = int(self.duration * 1000)  # s -> ms


class MqType(Enum):
    MQ = 'mq'
    MQTT = 'mqtt'
    KAFKA = 'kafka'

    def __repr__(self):
        return self.value


class MqHandleType(Enum):
    SEND = 'send'
    LISTEN = 'listen'

    def __repr__(self):
        return self.value


@dataclass
class MqLogExtra(BizLogExtra):
    cate: typing.Union[str, MqType] = None
    handle: MqHandleType = None

    def __post_init__(self):
        assert self.cate and self.cate in MqType
        assert self.handle and self.handle in MqHandleType
        self.cate = str(self.cate)
        if self.duration is not None:
            self.duration = int(self.duration * 1000)  # s -> ms
