![logo.png](logo.png)

# jiushu-logger【九书】

## 简介

JF 专用格式化 logger。 

听说有个人叫【九哥】，那我这个项目叫【九叔】很合理吧。（谐音梗扣钱！）

## 使用方法

引入包内所有内容：

```python
from jiushu_logger import *
```

使用包内的 ```Logger``` 类写日志，该类中包含 ```biz``` 、 ```req``` 、 ```call``` 、 ```cron``` 、 ```middleware``` 、 ```mq``` 等六种日志格式。
同时每种日志格式都有对应属于自己的 ```extra``` 参数配置。

使用方法如下：

（注意：req 日志是专用于 flask 和 starlette 插件包的，不供开发者自行使用。）

```python
from jiushu_logger import *

# 所有类型的日志均有 trace_id 和 duration 两项，但 trace_id 和 duration 均为非必需，duration 以秒为单位
Logger.biz.info('一个biz日志', extra=BizLogExtra(trace_id='xxx', duration=123.456))

# call 日志分为 INTERN 、 EXTERN 两种
Logger.call.warning('call警告', extra=CallLogExtra(cate=CallType.INTERN, call_params={'input': 'value1'},
                                                   call_resp={'output': 'value2'}))
Logger.call.warning('call警告', extra=CallLogExtra(cate=CallType.INTERN, call_params={'input': 'value1'},
                                                   call_resp={'output': 'value2'}))

# cron 日志适用于 xxl-job
Logger.cron.error('cron错误', extra=CronLogExtra(job_group='group', job_code='code'))

# middleware 日志分为 MYSQL 、 MONGO 、 REDIS 、 ES
Logger.middleware.debug('middleware调试', extra=MiddlewareLogExtra(cate=MiddlewareType.REDIS, host='x.x.x.x'))

# mq 日志分为 mq 、 mqtt 、 kafka , handle 分为 send 、 listen
Logger.middleware.info('', extra=MqLogExtra(cate=MqType.KAFKA, handle=MqHandleType.LISTEN))
Logger.middleware.info('', extra=MqLogExtra(cate=MqType.MQ, handle=MqHandleType.SEND))
```
