import ast
import base64
from io import BytesIO
from itertools import chain
from json import JSONDecodeError
from PIL import Image
import requests
from hashlib import md5

from data.session import LOGIN_SESSION
from data.url_conf import LOGIN_URL_MAPPING
from data.useragent import CHROME_USER_AGENT
from comonexception import ResponseError, ResponseCodeError
from data.const_data import FREE_CAPTCHA_CHECK_URL, FREE_CAPTCHA_HEADERS, FREE_CAPTCHA_URL

from utils.network import jsonStatus, sendRequests, getCaptchaImage
from utils.log import logger
from config import Config


class normalCaptchaUtil(object):
    success_code = '4'

    @staticmethod
    def getCaptcha():
        while True:
            try:
                data = getCaptchaImage(LOGIN_SESSION, LOGIN_URL_MAPPING["normal"]["captcha"])
                break
            except ResponseCodeError:
                logger.error("获取验证码信息失败,重试获取验证码中...")
                continue
        imageBinary = base64.b64decode(data["image"])
        return imageBinary

    def check(self, results):
        paramsData = {
            'answer': results,
            'rand': 'sjrand',
            'login_site': 'E'
        }
        while True:
            try:
                json_response = sendRequests(LOGIN_SESSION,
                                                      LOGIN_URL_MAPPING["normal"]["captchaCheck"],
                                                      data=paramsData)
                break
            except (ResponseCodeError, ResponseError):
                logger.error("提交验证码错误, 重新提交验证码验证")
                continue
        logger.info('验证码校验结果: %s' % json_response)
        status, msg = jsonStatus(json_response, [], ok_code=self.success_code)
        if not status:
            logger.error("验证码识别失败")
        return status, msg

class otherCaptchaUtil(object):
    success_code = '1'

    @staticmethod
    def getCaptcha():
        data = getCaptchaImage(LOGIN_SESSION, LOGIN_URL_MAPPING["other"]["captcha"])
        imgBinary = base64.b64decode(data["image"]).encode()
        return imgBinary

    def check(self, results):
        formData = {
            'randCode': results,
            'rand': 'sjrand',
        }

        jsonResponse = sendRequests(LOGIN_SESSION,
                                      LOGIN_URL_MAPPING["other"]["captchaCheck"],
                                      data=formData)
        logger.info('other login captcha verify: %s' % jsonResponse)

        def verify(response):
            return response['status'] and self.success_code == response['data']['result']

        v = verify(jsonResponse)
        return v, "Error" if not v else v

class Captcha(object):
    captcha = {"normal": normalCaptchaUtil(), "other": otherCaptchaUtil()}
    results = ''

    def __init__(self, loginType, method='hand'):
        self.loginType = loginType
        self.util = self.captcha[self.loginType]
        self.method = method

    def __getattribute__(self, item):
        if item in ("getCaptcha", "check"):
            return getattr(self.util, item)
        return object.__getattribute__(self, item)

    def generatorImage(self):
        while True:
            data = self.getCaptcha()
            try:
                img = Image.open(BytesIO(data))
                img.close()
                break
            except OSError:
                logger.error("获取验证码图片失败, 重试获取")
                continue
        
        return data

    @staticmethod
    def trans_captcha_results(indexes, sep=r','):
        coordinates = ['40,40', '110,40', '180,40', '250,40',
                       '40,110', '110,110', '180,110', '250,110']
        results = []
        for index in indexes.split(sep=sep):
            results.append(coordinates[int(index)])
        return ','.join(results)


    def verify(self):
        if Config.auto_code_enable:
            logger.info("采用打码平台进行验证码")
        
        m = getattr(self, "verifyhandle_{method}".format(method=self.method))
        return m()
    
    def verifyhandle_hand(self):
        img = Image.open(BytesIO(self.generatorImage()))
        if not Config.save_img_enable:
            img.show()
        else:
            img.save('captcha.jpg')
        logger.info( 
            """
            -----------------
            | 0 | 1 | 2 | 3 |
            -----------------
            | 4 | 5 | 6 | 7 |
            ----------------- """)

        results = input("输入验证码索引(见上图，以','分割）: ")
        img.close()

        trans = self.trans_captcha_results(results)
        self.results = trans
        return self.check(trans)

