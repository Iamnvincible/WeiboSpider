import base64
import binascii
import datetime
import json
import math
import os
import random
import re
import time
from urllib.parse import quote_plus

import requests
import rsa

from config.headers import headers
from utils import getIP
from web import get_pin_code_img


def get_pincode_url(pcid):
    size = 0
    url = "http://login.sina.com.cn/cgi/pin.php"
    pincode_url = '{}?r={}&s={}&p={}'.format(
        url, math.floor(random.random() * 100000000), size, pcid)
    return pincode_url


def get_encodename(name):
    # name must be string
    username_quote = quote_plus(str(name))
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))
    return username_base64.decode("utf-8")


# prelogin for servertime, nonce, pubkey, rsakv
def get_server_data(su, session, proxy):
    pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
    pre_url = pre_url + su + \
        "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
    prelogin_url = pre_url + str(int(time.time() * 1000))
    pre_data_res = session.get(prelogin_url, headers=headers, proxies=proxy)

    sever_data = eval(pre_data_res.content.decode(
        "utf-8").replace("sinaSSOController.preloginCallBack", ''))

    return sever_data


def get_password(password, servertime, nonce, pubkey):
    rsa_publickey = int(pubkey, 16)
    key = rsa.PublicKey(rsa_publickey, 65537)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
    message = message.encode("utf-8")
    passwd = rsa.encrypt(message, key)
    passwd = binascii.b2a_hex(passwd)
    return passwd


# post data and get the next url
def get_redirect(name, data, post_url, session, proxy):
    logining_page = session.post(
        post_url, data=data, headers=headers, proxies=proxy)
    login_loop = logining_page.content.decode("GBK")

    # if name or password is wrong, set the value to 2
    if 'retcode=101' in login_loop:
        print(
            'invalid password for {}, please ensure your account and password'.format(name))
        return ''

    if 'retcode=2070' in login_loop:
        print('invalid verification code')
        return 'pinerror'

    if 'retcode=4049' in login_loop:
        print('account {} need verification for login'.format(name))
        return 'login_need_pincode'

    if '正在登录' in login_loop or 'Signing in' in login_loop:
        pa = r'location\.replace\([\'"](.*?)[\'"]\)'
        return re.findall(pa, login_loop)[0]
    else:
        return ''


def login_no_pincode(name, password, session, server_data, proxy):
    post_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

    servertime = server_data["servertime"]
    nonce = server_data['nonce']
    rsakv = server_data["rsakv"]
    pubkey = server_data["pubkey"]
    sp = get_password(password, servertime, nonce, pubkey)

    data = {
        'encoding': 'UTF-8',
        'entry': 'weibo',
        'from': '',
        'gateway': '1',
        'nonce': nonce,
        'pagerefer': "",
        'prelt': 67,
        'pwencode': 'rsa2',
        "returntype": "META",
        'rsakv': rsakv,
        'savestate': '7',
        'servertime': servertime,
        'service': 'miniblog',
        'sp': sp,
        'sr': '1920*1080',
        'su': get_encodename(name),
        'useticket': '1',
        'vsnf': '1',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'
    }

    rs = get_redirect(name, data, post_url, session, proxy)

    return rs, session


def login_by_pincode(name, password, session, server_data, retry_count, proxy):
    post_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

    servertime = server_data["servertime"]
    nonce = server_data['nonce']
    rsakv = server_data["rsakv"]
    pubkey = server_data["pubkey"]
    pcid = server_data['pcid']

    sp = get_password(password, servertime, nonce, pubkey)

    data = {
        'encoding': 'UTF-8',
        'entry': 'weibo',
        'from': '',
        'gateway': '1',
        'nonce': nonce,
        'pagerefer': "",
        'prelt': 67,
        'pwencode': 'rsa2',
        "returntype": "META",
        'rsakv': rsakv,
        'savestate': '7',
        'servertime': servertime,
        'service': 'miniblog',
        'sp': sp,
        'sr': '1920*1080',
        'su': get_encodename(name),
        'useticket': '1',
        'vsnf': '1',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'pcid': pcid
    }

    print('Login need verfication code')
    img_url = get_pincode_url(pcid)
    # TODO 下载验证码
    get_pin_code_img(img_url)
    verify_code = input('please input pin code')
    data['door'] = verify_code
    rs = get_redirect(name, data, post_url, session, proxy)

    return rs, session


def login_retry(name, password, session,  proxy, rs='pinerror', retry_count=0):
    while rs == 'pinerror':
        retry_count += 1
        session = requests.Session()
        su = get_encodename(name)
        server_data = get_server_data(su, session, proxy)
        rs, session = login_by_pincode(
            name, password, session, server_data, retry_count, proxy)
    return rs, session


def do_login(name, password, proxy):
    session = requests.Session()
    su = get_encodename(name)
    server_data = get_server_data(su, session, proxy)

    if server_data['showpin']:
        rs, yundama_obj, cid, session = login_by_pincode(
            name, password, session, server_data, 0, proxy)
        if rs == 'pinerror':
            rs, yundama_obj, cid, session = login_retry(
                name, password, session, yundama_obj, cid, proxy)

    else:
        rs, session = login_no_pincode(
            name, password, session, server_data, proxy)
        if rs == 'login_need_pincode':
            session = requests.Session()
            su = get_encodename(name)
            server_data = get_server_data(su, session, proxy)
            rs, session = login_by_pincode(
                name, password, session, server_data, 0, proxy)

            if rs == 'pinerror':
                rs, session = login_retry(
                    name, password, session,  proxy)

    return rs, session


def get_session(name, password):
    proxy = getIP("")

    url, session = do_login(name, password, proxy)

    if url != '':
        rs_cont = session.get(url, headers=headers, proxies=proxy)
        login_info = rs_cont.text

        u_pattern = r'"uniqueid":"(.*)",'
        m = re.search(u_pattern, login_info)
        if m and m.group(1):
            check_url = 'http://weibo.com/2671109275/about'
            session.get(check_url, headers=headers, proxies=proxy)
            print('Login successful! The login account is {}'.format(name))
            pickled_cookies = json.dumps(
                {'cookies': session.cookies.get_dict(), 'loginTime': datetime.datetime.now().timestamp(), 'proxy': proxy['http']})
            with open('cookie', 'w') as file:
                file.write(pickled_cookies)
            return session

    print('login failed for {}'.format(name))
    return None
