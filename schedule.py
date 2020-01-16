import datetime
import time
from itertools import product

from config import Config
from utils.log import logger
from logic.login.login import normalLogin

from utils.cdn import cdnHandle


class Schedule(object):
    retryLoginTimes = Config.basic_config.retry_login_time
    order_id = ''
    unfinished_order = False
    order_tickets = []

    def login(self):
        count = 0
        while self.retryLoginTimes >= count:
            loginInstance = normalLogin()
            logger.info("正在为您登录")
            status, msg = loginInstance.login()

            count += 1
        return True

    @staticmethod
    def query_passengers():
        return True
    @staticmethod
    def checkMaintain():
        now = datetime.datetime.now()
        morningTime = datetime.datetime(year=now.year,
                                        month=now.month,
                                        day=now.day,
                                        hour=6,
                                        minute=0
                                    )
        eveningTime = datetime.datetime(year=now.year,
                                         month=now.month,
                                         day=now.day,
                                         hour=23,
                                         minute=0
                                         )                            
        if now > eveningTime or now < morningTime:
            return True
        else:
            return False

    @staticmethod
    def deltaMaintainTime():
        now = datetime.datetime.now()
        morningTime = datetime.datetime(year=now.year,
                                         month=now.month,
                                         day=now.day,
                                         hour=5,
                                         minute=59,
                                         second=56
                                         )
        nextMorningTime = datetime.datetime(year=now.year,
                                              month=now.month,
                                              day=now.day,
                                              hour=5,
                                              minute=59,
                                              second=56
                                              ) + datetime.timedelta(days=20)
        eveningTime = datetime.datetime(year=now.year,
                                         month=now.month,
                                         day=now.day,
                                         hour=23,
                                         minute=0
                                         )
        if now > eveningTime:
            return nextMorningTime - now
        elif now < morningTime:
            return morningTime - now

    def mainMode(self):
        if self.checkMaintain():
            logger.info("12306系统每天 23:00 - 6:00 之间 维护中, 程序暂时停止运行")
        
        mainTime = self.deltaMaintainTime()
        if not mainTime:
            return 
        logger.info("{0}小时 {1}分钟 {2}秒之后重新启动".format(
                mainTime.seconds // 3600,
                (mainTime.seconds // 60) % 60,
                mainTime.seconds % 3600 % 60))

        time.sleep(self.deltaMaintainTime().total_seconds())

    def preCheck(self):
        if Config.cdn_enable:
            cdnHandle.load_exists()

        if not self.login():
            return False
        
        passengerStatus = self.query_passengers()

        if not passengerStatus:
            return False
            
        if not Config.auto_code_enable:
            logger.info("未开启自动打码功能, 不检测用户登录状态")

        return True
        

    def run(self):
        self.mainMode()
        status = self.preCheck()
        if not status:
            return 





def main():
    instance = Schedule()
    instance.run()

if __name__ == "__main__":
    main()