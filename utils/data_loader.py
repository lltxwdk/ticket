import os
import datetime
import pickle

class localSimpleCache(object):
    """
    param: 

    rawData: 需要导出的数据
    pickleName: 导出的pickle名称
    expireTime: 过期时间, 单位小时

    """
    def __init__(self, rawData, pickleName, expireTime = 24):
        self.current = datetime.datetime.now()
        self.rawData = rawData
        self.pickleName = pickleName
        self.expireTime = expireTime

    def isExistsPickle(self):
        return os.path.exists(self.picklePath)

    @property
    def picklePath(self):
        return os.path.join(
            os.path.abspath(os.getcwd()),
            self.pickleName)

    def exportPickle(self):
        with open(os.path.join(self.picklePath), 'wb') as handle:
        #序列化对象，将对象obj保存到文件file中去。
            pickle.dump(self, handle)
    
    def loadExistsData(self):

        if self.isExistsPickle():
            with open(os.path.join(self.picklePath), 'rb') as handle:
            #反序列化对象，将文件中的数据解析为一个python对象。file中有read()接口和readline()接口
                result = pickle.load(handle)

            result.current = datetime.datetime.fromtimestamp(os.path.getmtime(self.picklePath))
            return result

    def getFinalData(self):

        result = self.loadExistsData()

        if result and result.rawData:

            if result.current + datetime.timedelta(hours=self.expireTime) > self.current:
                return result
        self.exportPickle()
        return self
        


