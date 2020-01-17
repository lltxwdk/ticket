import copy
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import requests
import urllib3
from urllib3.util import parse_url

from utils.log import logger
from comonexception import ResponseError, ResponseCodeError

def getCaptchaImage(session, urlMappingObj, params=None, data=None, **kwargs):
    """
    xml data example:
        <HashMap>
            <result_message>生成验证码成功</result_message>
            <result_code>0</result_code>
            <image>imagedata<image>
        </HashMap>
        format result data.
    """
    session.headers.update(urlMappingObj.headers)
    try:
        response = session.request(
            method=urlMappingObj.method,
            url=urlMappingObj.url,
            params=params,
            data=data,
            timeout=10,
            **kwargs
        )
    except requests.RequestException as e:
        logger.info(e)
        logger.info("请求{0}异常 ".format(urlMappingObj.url))
        raise ResponseError
    if response.status_code == requests.codes.ok:
        if 'xhtml+xml' in response.headers['Content-Type']:
            data = response.text
            root = ET.fromstring(data)
            message = root.find('result_message').text
            code = root.find('result_code').text
            image = root.find('image').text
            return {"result_message": message, "code": code, 'image': image}
        elif 'json' in response.headers['Content-Type']:
            return response.json()
        else:
            logger.info(response.url)
            logger.info(response.status_code)
            raise ResponseCodeError
    else:
        logger.error(response.url)
        logger.error(response.status_code)
        raise ResponseCodeError

def sendRequests(session, urlMappingObj, params=None, data=None, **kwargs):
    session.headers.update(urlMappingObj.headers)
    if urlMappingObj.method.lower() == 'post':
        session.headers.update(
            {"Content-Type": r'application/x-www-form-urlencoded; charset=UTF-8'}
        )
    else:
        session.headers.pop("Content-Type", None)
    #cdn 暂时不加
    
    requestUrl = urlMappingObj.url

    try:
        logger.info("请求 url {url}".format(url=requestUrl))
        try:
            response = session.request(method=urlMappingObj.method,
                                           url=requestUrl,
                                           params=params,
                                           data=data,
                                           timeout=10,
                                           **kwargs)
        except requests.RequestException as e:
            logger.error(e)
            logger.error("请求{0}异常 ".format(requestUrl))
            raise ResponseError
        logger.info("{url} Get 参数 {data}".format(url=requestUrl,
                                               data=params))
        logger.info("{url} Post 参数 {data}".format(url=requestUrl,
                                                data=data))
        logger.info("返回response url {url}".format(url=response.url))
        if response.status_code == requests.codes.ok:
            if 'xhtml+xml' in response.headers['Content-Type']:
                data = response.text
                root = ET.fromstring(data)
                result = {v.tag: v.text for v in root.getchildren()}
                return result
            if 'json' in response.headers['Content-Type'] and urlMappingObj.type.lower() != 'text':
                result = response.json()
                logger.info("{url} 返回值 {result}".format(url=response.url,
                                                  result=result))
                return result
            # other type
            return response.text
        elif response.status_code == requests.codes.found:
            if 'leftTicket/query' in requestUrl and 'json' in response.headers['Content-Type']:
                logger.info("检测到查票接口有变, 更改为新的查票接口")
                result = response.json()
                try:
                    url = result["c_url"]
                    urlMappingObj.url = urljoin("https://kyfw.12306.cn/otn/", url)
                except KeyError:
                    logger.info(response.url)
                    logger.info(response.status_code)
                    logger.info("更改查票接口失败")
            else:
                logger.info(response.url)
                logger.info(response.status_code)
                logger.info("返回状态码有问题")
        else:
            logger.info(response.url)
            logger.info(response.status_code)
            logger.info("返回状态码有问题")
    except Exception as e:
        logger.info(e)

    return None


def jsonStatus(json_response, check_column, ok_code=0):
    """
    :param ok_code: ok code.
    :param json_response: json_response
    :param check_column: check column, add column missing message
    :return:
    """
    if not isinstance(json_response, (list, dict)):
        return False, '数据非json数据'

    code = json_response.get('result_code',None)
    status = code == ok_code or code == 0 or code == '0'

    if status:
        return status,"OK"
    else:
        return status, " ".join(["{column} not found".format(
            column=v
        ) for v in check_column if v not in json_response])




