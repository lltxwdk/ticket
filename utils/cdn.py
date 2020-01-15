import copy
import math
import random
import socket
import time

from multiprocessing.pool import ThreadPool
from threading import Lock

import requests
import urllib3

from resources.cdn_list import CDN_LIST


from urllib3.exceptions import SSLError, MaxRetryError

from utils.log import logger



class cdnCheck(object):
    def __init__(self):
        self.raw_cdn_list = copy.copy(CDN_LIST)
        self.result = []
        self.status = False
        self.pool = ThreadPool(10)
        self.lock = Lock()
        self.max_available_level = 5

    def load_exists(self):
        return True

cdnHandle = cdnCheck()