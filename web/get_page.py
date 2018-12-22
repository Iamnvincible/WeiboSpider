import os
import time
import signal
import json
import requests

from web import is_404, is_403, is_complete, is_banned
from utils import getIP, getIPWithoutLogin, generate_rnd

from config import (headers, time_out, min_crawl_interal,
                    max_crawl_interal, excp_interal, max_retries)
TIME_OUT = time_out
INTERAL = min_crawl_interal
MAX_RETRIES = max_retries
EXCP_INTERAL = excp_interal


def get_page(url, is_ajax=False, need_proxy=False):
    """
    :param url: 请求页面url
    :param is_ajax: whether the request is ajax
    :param need_proxy: whether the request need a http/https proxy
    :return: 返回相应正文，异常则返回 None
    """
    print('Requesting url {}'.format(url))
    count = 0

    while count < MAX_RETRIES:
        try:
            with open('cookie', 'r') as file:
                name_cookies = file.read()
                name_cookies = json.loads(name_cookies)
                name_cookies = list(name_cookies.values())
        except Exception as e:
            print('{Exception raised when processing cookie}', format(e))
        # There is no difference between http and https address.
        proxy = {'http': name_cookies[2], 'https': name_cookies[2], }
        try:
            resp = requests.get(
                url, headers=headers, cookies=name_cookies[0], timeout=TIME_OUT, verify=False, proxies=proxy)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, AttributeError) as e:
            print(
                'Excepitons are raised when crawling {}.Here are details:{}'.format(url, e))
            count += 1
            time.sleep(EXCP_INTERAL)
            # try again
            continue

        if resp.status_code == 414:
            print('This ip has been blocked by weibo system')
        if resp.text:
            page = resp.text.encode('utf-8', 'ignore').decode('utf-8')
        else:
            count += 1
            continue
            # slow down to aviod being banned  XD
        time.sleep(INTERAL/5)
        if is_banned(resp.url) or is_403(page):
            print('Account {} has been banned'.format(name_cookies[0]))
            count += 1
            continue

        if is_ajax and not is_complete(page):
            count += 1
            continue

        if is_404(page):
            print('{} seems to be 404 NOT FOUND'.format(url))
            return None
        return page

    return None


def get_long_text(weibo_id):
    try:
        base_url = 'https://weibo.com/p/aj/mblog/getlongtext'
        assembled_long_text_url = '{}?ajwvr=6&mid={}&__rnd={}'.format(
            base_url, weibo_id, generate_rnd())
        resp = get_page(assembled_long_text_url)
        resp = json.loads(resp)['data']['html']
        return resp
    except:
        return None


def get_pin_code_img(url):
    r = requests.get(url)
    with open('pin.jpg','wb') as file:
        file.write(r.content)
