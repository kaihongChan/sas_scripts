import datetime
import requests
from requests.utils import dict_from_cookiejar
from http import cookiejar

import sys


sys.path.append("/app/scripts/")
from app.common.login import Login
from conf import COOKIE_PATH


def get_yesterday():
    """
    昨日日期
    :return:
    """
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    yesterday = today - one_day
    return yesterday


def request_get(account, url, headers, params):
    """
    get请求
    :param account:
    :param url:
    :param headers:
    :param params:
    :return:
    """
    try:
        Login().login(account['username'], account['password'])
        cookie_file_name = f"{COOKIE_PATH}/cookie_{account['username']}.txt"
        session = requests.session()
        cookie = cookiejar.LWPCookieJar()
        cookie.load(cookie_file_name, ignore_discard=True, ignore_expires=True)
        cookie = dict_from_cookiejar(cookie)
        session.cookies = requests.utils.cookiejar_from_dict(cookie)
        session.headers = headers
        resp = session.get(url, params=params)
        return resp
    except Exception as e:
        raise Exception(e)
