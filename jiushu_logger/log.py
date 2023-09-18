# coding: utf-8
import logging
import sys
import typing
from enum import Enum

from .helpers import safely_jsonify

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


class Logger:
    biz = _init_logger('biz', _biz_format)
    req = _init_logger('req', _req_format)
    call = _init_logger('call', _call_format)
    cron = _init_logger('cron', _cron_format)
    middleware = _init_logger('middleware', _middleware_format)
    mq = _init_logger('mq', _mq_format)


class _BaseLogExtra(typing.Mapping):
    def __init__(self, trace_id: str, duration: float):
        self.trace_id = trace_id
        self.duration = (int(duration * 1000)
                         if duration is not None
                         else None)  # Convert seconds to milliseconds

    def __getitem__(self, field_name):
        return getattr(self, field_name)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __iter__(self):
        yield from (key for key in self.__dict__)


# ----- 业务日志 -----
class BizLogExtra(_BaseLogExtra):
    def __init__(self, trace_id: str = None, duration: float = None):
        super().__init__(trace_id, duration)
        self.cate = 'biz'


# ----- 请求日志 -----
class ReqLogExtra(_BaseLogExtra):
    def __init__(self,
                 trace_id: str = None, duration: float = None,
                 method: str = None, path: str = None, client_ip: str = None, host: str = None,
                 headers: str = None, query: str = None, body: str = None, resp: str = None):
        super().__init__(trace_id, duration)
        self.cate = 'req'
        self.method = method
        self.path = path
        self.client_ip = client_ip
        self.host = host
        self.headers = headers
        self.query = query
        self.body = body
        self.resp = resp


# ----- 调用日志 -----
class CallType(Enum):
    INTERN = 'internalCall'
    EXTERN = 'externalCall'


class CallLogExtra(_BaseLogExtra):
    def __init__(self,
                 trace_id: str = None, duration: float = None,
                 type: CallType = CallType.INTERN, params: typing.Mapping = None, resp: typing.Mapping = None):
        super().__init__(trace_id, duration)
        self.cate = type.value
        self.call_params = safely_jsonify(params) if params is not None else None
        self.call_resp = safely_jsonify(resp) if resp is not None else None


# ----- 计划任务日志 -----
class CronLogExtra(_BaseLogExtra):
    def __init__(self,
                 trace_id: str = None, duration: float = None,
                 job_group: str = None, job_code: str = None):
        super().__init__(trace_id, duration)
        self.cate = 'cron'
        self.job_group = job_group
        self.job_code = job_code


# ----- 中间件日志 -----
class MiddlewareType(Enum):
    MYSQL = 'mysql'
    MONGO = 'mongo'
    REDIS = 'redis'
    ES = 'es'


class MiddlewareLogExtra(_BaseLogExtra):
    def __init__(self,
                 trace_id: str = None, duration: float = None,
                 type: MiddlewareType = MiddlewareType.MYSQL, host: str = None):
        super().__init__(trace_id, duration)
        self.cate = type.value
        self.host = host


# ----- 对列日志 -----
class MqType(Enum):
    MQ = 'mq'
    MQTT = 'mqtt'
    KAFKA = 'kafka'


class MqHandleType(Enum):
    SEND = 'send'
    LISTEN = 'listen'


class MqLogExtra(_BaseLogExtra):
    def __init__(self,
                 trace_id: str = None, duration: float = None,
                 type: MqType = MqType.MQ, handle_type: MqHandleType = MqHandleType.LISTEN):
        super().__init__(trace_id, duration)
        self.cate = type.value
        self.handle = handle_type.value
