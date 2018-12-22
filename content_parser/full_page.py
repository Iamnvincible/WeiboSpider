from utils import generate_rnd
from web import get_page
from content_parser import get_data, get_max_num, get_user_id, get_weibo_list
from content_parser.user_info.public import get_userid
import json


def get_person_one_full_page(pagenum, userid=None, name=None):
    page_weibo = []
    page = pagenum
    base_url_uid = 'https://www.weibo.com/u'
    base_url_name = 'https://www.weibo.com'
    if userid:
        base_url = base_url_uid
        para = userid
    elif name:
        base_url = base_url_name
        para = name
    else:
        return page_weibo
    assembled_url = '{}/{}?page={}'.format(base_url, para, page)
    first_req_html = get_page(assembled_url)
    userid = userid if userid else get_userid(first_req_html)
    page_weibo.extend(get_data(first_req_html, userid))
    page_sum = get_max_num(first_req_html)
    #page_sum = -1
    if page_sum == -1 and len(page_weibo) > 0:
        bar = 0
        weibo_html_0, weibo_list_0 = get_pagebar(userid, page, bar)
        weibo_html_1, weibo_list_1 = get_pagebar(
            userid, page, bar+1)
        if(len(weibo_html_0) != len(weibo_html_1)):
            weibo_list_0.extend(weibo_list_1)
            page_weibo.extend(weibo_list_0)
            # with open('weibohtml0.html', 'w', encoding='utf-8') as file:
            #     file.write(weibo_html_0)
            # with open('weibohtml1.html', 'w', encoding='utf-8') as file:
            #     file.write(weibo_html_1)

    return page_weibo


def get_pagebar(userid, pagenum, bar):
    more_feed_base_url = 'https://weibo.com/p/aj/v6/mblog/mbloglist'
    ajwvr = 6
    domain = 100505
    # refer_flag = '1005055013_'  # 不必须
    is_all = 1
    pagebar = bar  # key para
    # pl_name = 'Pl_Official_MyProfileFeed__19'
    domain = 100505
    uid = userid
    # script_uri = username  # 不必须
    feed_type = 0
    page = pagenum
    pre_page = page
    domain_op = domain
    rnd = generate_rnd()
    assembled_more_feed_url = '{}?ajwvr={}&domain={}&is_all={}&pagebar={}&id={}&feed_type={}&page={}&pre_page={}&domain_op={}&_rnd={}'.format(
        more_feed_base_url, ajwvr, domain, is_all, pagebar, str(domain)+str(uid), feed_type, page, pre_page, domain_op, rnd)
    # ?ajwvr=6&domain=100505&refer_flag=1005055013_&is_all=1&pagebar=1&pl_name=Pl_Official_MyProfileFeed__19&
    # id=1005051340724027&script_uri=/tiancaixinxin&feed_type=0&page=2&pre_page=2&domain_op=100505&__rnd=1544605567059'
    html = get_page(assembled_more_feed_url)
    weibo_html = json.loads(html)['data']
    weibos = get_weibo_list(weibo_html)
    return weibo_html, weibos
