import ast
import re
import time
import os
from urllib import parse
from utils.log import logger

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from logic.login.captcha import Captcha

from utils.data_loader import localSimpleCache
from utils.network import sendRequests, jsonStatus
from config import Config

from data.session import LOGIN_SESSION
from data.url_conf import LOGIN_URL_MAPPING

def getFingerprint(driver):
    return driver.current_url == "https://kyfw.12306.cn/otn/resources/login.html"


class normalLogin(object):

    __session = LOGIN_SESSION
    URLS = LOGIN_URL_MAPPING["normal"]

    def init(self):
        temp = localSimpleCache([], "device_pickle.pickle", expireTime=24)
        load = temp.getFinalData()
        chromeDriver = os.path.join(os.getcwd(),'conf\\chromedriver.exe')

        if not load.rawData:
            logger.info("使用selenium获取完整cookie")
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument("--incognito")
            options.add_argument("--disable-databases")
            options.add_argument("--disable-gpu-compositing")
            options.add_argument("--disable-application-cache")
            driver = webdriver.Chrome(executable_path=chromeDriver,options=options)
            driver.implicitly_wait(15)
            # first clear selenium cache
            driver.get("https://kyfw.12306.cn")
            wait = WebDriverWait(driver, 10)
            wait.until(getFingerprint)

            cookies = driver.get_cookies()
            driver.quit()
            if "RAIL_DEVICEID" not in [v["name"] for v in cookies] \
                or "RAIL_EXPIRATION" not in [v["name"] for v in cookies]:
                return False, "设备指纹未获取到"
            temp.rawData = [v for v in cookies]
            logger.info("导出包含设备指纹的cookie")
            temp.exportPickle()
        else:
            logger.info("使用缓存过的cookie")
            cookies = load.rawData

        for value in cookies:
            value.pop('httpOnly', None)
            value.pop('expiry', None)
            LOGIN_SESSION.cookies.set(**value)
        logger.info("已经获取设备指纹")
        return True, "已经获取设备指纹"

    def passPortRedirect(self):
        sendRequests(LOGIN_SESSION, self.URLS["userLoginRedirect"])

    def uamTk(self):
        jsonData = sendRequests(LOGIN_SESSION, self.URLS["uamtk"], data={'appid': 'otn'})
        logger.info(jsonData)
        result, msg = jsonStatus(jsonData, ["result_message", "newapptk"])
        if not result:
            return result, msg, None
        else:
            return result, msg, jsonData["newapptk"]

    def uamAuthClient(self, apptk):
        jsonResponse = sendRequests(LOGIN_SESSION, self.URLS['uamauthclient'], data={'tk': apptk})
        status, msg = jsonStatus(jsonResponse, ["username", "result_message"])
        if status:
            logger.info("欢迎 {0} 登录".format(jsonResponse["username"]))
        return status, msg

    def login(self):
        if not LOGIN_SESSION.cookies.get("RAIL_EXPIRATION") or \
           not LOGIN_SESSION.cookies.get("RAIL_DEVICEID"):
            status, msg = self.init()
            if not status:
                return status, msg

        captcha = Captcha("normal")
        status, msg = captcha.verify()
        if not status:
            logger.info("验证码校验失败")
            return status,msg

        payload = {
            'username': Config.train_account.user,
            'password': Config.train_account.pwd,
            'appid': 'otn',
            'answer': captcha.results
        }

        jsonResponse = sendRequests(LOGIN_SESSION, self.URLS['login'], data=payload)
        result, msg = jsonStatus(jsonResponse, [], '0')

        if not result:
            return (False, jsonResponse.get("result_message", None)) \
                if isinstance(jsonResponse, dict) else (False, '登录接口提交返回数据出现问题')

        self.passPortRedirect()
        result, msg, apptk = self.uamTk()

        if not result:
            logger.info(msg)
            return False, msg
        status, msg = self.uamAuthClient(apptk)
        return status, msg




          
