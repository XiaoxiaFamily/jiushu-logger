# coding: utf-8
from .log import *

try:
    import flask
    from .flask_log import *
except:
    pass

try:
    import starlette
    from .starlette_log import *
except:
    pass
