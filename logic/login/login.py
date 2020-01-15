import ast
import re
import time
from urllib import parse

from data.session import LOGIN_SESSION
from data.url_conf import LOGIN_URL_MAPPING

class normalLogin(object):

    __session = LOGIN_SESSION
    URLS = LOGIN_URL_MAPPING["normal"]