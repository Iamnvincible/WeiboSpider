import re
from bs4 import BeautifulSoup
from utils import url_filter, url_simplify
from config import ROOT_URL, PROTOCOL
from web import get_long_text, get_page
from model import WeiboData
import json
import urllib


def get_weibo_infos_right(html):
    """
    通过网页获取用户主页右边部分（即微博部分）字符串
    :param html:
    :return:
    """
    soup = BeautifulSoup(html, "lxml")
    scripts = soup.find_all('script')
    pattern = re.compile(r'FM.view\((.*)\)')

    # 如果字符串'fl_menu'(举报或者帮上头条)这样的关键字出现在script中，则是微博数据区域
    cont = ''
    for script in scripts:
        m = pattern.search(script.string)
        if m and 'fl_menu' in script.string:
            print('get weibo part!')
            all_info = m.group(1)
            cont += json.loads(all_info).get('html', '')
    return cont


def get_weibo_list(html, target_uid=None):
    """
    get the list of weibo info
    :param html:
    :return: 
    """
    if not html:
        return list()
    soup = BeautifulSoup(html, "lxml")
    feed_list = soup.find_all(attrs={'action-type': 'feed_list_item'})
    weibo_datas = []
    for data in feed_list:
        r = get_weibo_info_detail(data, target_uid)
        if r is not None:
            #wb_data = r
            # if r[1] == 0 and CRAWLING_MODE == 'accurate':
            #     weibo_cont = status.get_cont_of_weibo(wb_data.weibo_id)
            #     wb_data.weibo_cont = weibo_cont if weibo_cont else wb_data.weibo_cont
            weibo_datas.append(r)
    return weibo_datas


def get_data(html, target_uid=None):
    """
    从主页获取具体的微博数据
    :param html: 
    :return: 
    """
    cont = get_weibo_infos_right(html)
    return get_weibo_list(cont, target_uid)


def get_max_num(html):
    """
    get the total page number
    :param html:
    :return:
    """
    soup = BeautifulSoup(html, "lxml")
    href_list = soup.find(
        attrs={'action-type': 'feed_list_page_morelist'})
    if href_list:
        href_list.find_all('a')
        return len(href_list)
    else:
        return -1


def get_ajax_data(html):
    """
    通过返回的ajax内容获取用户微博信息
    :param html: 
    :return: 
    """
    cont = json.loads(html, encoding='utf-8').get('data', '')
    return get_weibo_list(cont)


def get_total_page(html):
    """
    从ajax返回的内容获取用户主页的所有能看到的页数
    :param html: 
    :return: 
    """
    cont = json.loads(html, encoding='utf-8').get('data', '')
    if not cont:
        # todo 返回1或者0还需要验证只有一页的情况
        return 1
    return get_max_num(cont)


def get_user_id(feed_list_item):
    """
    从微博中获得用户id
    :param each:单条微博的feed_list_item下的html
    :return:用户id
    """
    user_cont = feed_list_item.find(attrs={'class': 'face'})
    if user_cont:
        user_info = str(user_cont.find('a'))
        user_pattern = 'id=(\\d+)&amp'
        m = re.search(user_pattern, user_info)
        if m:
            return m.group(1)
        else:
            print("fail to get user'sid")
            return None


def get_user_name(feed_list_item):
    """
    从微博中获得用户名
    :param each:单条微博的feed_list_item下的html
    :return:用户名
    """
    user_cont = feed_list_item.find(attrs={'class': 'face'})
    if user_cont:
        user_info = user_cont.find('a')
        if user_info:
            return user_info.get('title')
    return ''


def get_weibo_id(feed_list_item):
    """
    获得微博id
    :param each: 单条微博的feed_list_item下的html
    :return: 微博id
    """
    weibo_pattern = 'mid=(\\d+)'
    m = re.search(weibo_pattern, str(feed_list_item))
    if m:
        return m.group(1)
    else:
        print("fail to get weibo's id")
        return None


def get_create_time(feed_list_item):
    """
    获得微博发布时间
    :param feed_list_item: 单条微博的feed_list_item下的html
    """
    time_url = feed_list_item.find(attrs={'node-type': 'feed_list_item_date'})
    if time_url:
        return time_url.get('title', '')
    else:
        return None


def get_weibo_url(feed_list_item):
    """
    获取单条微博链接
    :param feed_list_item: 单条微博的feed_list_item下的html
    """
    time_url = feed_list_item.find(attrs={'node-type': 'feed_list_item_date'})
    if time_url:
        weibo_url = time_url.get('href', '')
        if ROOT_URL not in weibo_url:
            weibo_url = '{}://{}{}'.format(
                PROTOCOL, ROOT_URL, weibo_url)
        return url_simplify(weibo_url)
    else:
        return None


def get_weibo_imgs(feed_content, is_repost):
    """
    获取微博配图链接
    :param feed_content: 单条微博feed_content下的html
    :param is_repost: 是否为转发
    :return: 图片链接列表
    """
    imglist = []
    if is_repost:
        # 如果这是一条转发，不获取链接
        return imglist
    else:
        try:
            imgs = str(feed_content.find(
                attrs={'node-type': 'feed_list_media_prev'}).find_all('img'))
            imgs_url = map(url_filter, re.findall(r"src=\"(.+?)\"", imgs))
            for item in imgs_url:
                imglist.append(item)
            return imglist
        except:
            return imglist


def get_weibo_clip(feed_content, is_repost):
    """
    获取微博配的视频
    :param feed_content: 单条微博feed_content下的html
    :param is_repost: 是否为转发
    :return: 微博所配视频链接
    """
    clip = ""
    if is_repost:
        return clip
    else:
        try:
            li = str(feed_content.find(attrs={'node-type': 'feed_list_media_prev'}).
                     find_all('li'))
            extracted_url = urllib.parse.unquote(
                re.findall(r"video_src=(.+?)&amp;", li)[0])
            return url_filter(extracted_url)
        except:
            return clip


def replace_face_with_text(feed_content, has_long_text):
    """
    替换微博内容中的微博表情为特定文本：[表情:[允悲]]
    :param feed_content: 单条微博feed_content下的html
    :param has_long_text: 是否有展开全文
    """
    if feed_content and not has_long_text:
        faces = feed_content.find(
            attrs={'node-type': 'feed_list_content'}).find_all(attrs={'type': 'face'})
        if len(faces) > 0:
            for face in faces:
                face.string = '[表情:'+face.get('title')+']'


def replace_face_with_text_long(long_text_html):
    """
    替换微博内容中的微博表情为特定文本：[表情:[允悲]]
    :param feed_content: 单条微博feed_content下的html
    """
    if long_text_html:
        faces = long_text_html.find_all(attrs={'type': 'face'})
        if len(faces) > 0:
            for face in faces:
                face.string = '[表情:'+face.get('title')+']'


def mark_and_get_links(feed_content, is_repost, has_long_text):
    """
    获取微博中出现的链接
    将链接标记成特定文本：[链接:xxx]
    :param feed_content: 单条微博feed_content下的html
    :param is_repost: 是否为转发
    :param has_long_text: 是否有展开全文
    :return:微博中出现的链接列表
    """
    hyper_links = []
    if feed_content:
        # 如果是条转发/没有展开全文，直接获取正文中的链接
        # 不是转发
        #   如果有展开全文
        #       获取全文后再标记,不在这里处理
        if is_repost or not has_long_text:
            links = feed_content.find(
                attrs={'node-type': 'feed_list_content'}).find_all('a')
            if len(links) > 0:
                for item in links:
                    hyper_links.append(item.get('href'))
                    item.string = '[链接:'+item.text+']'
                return [url_simplify(item) for item in map(url_filter, hyper_links)]
    return hyper_links


def mark_and_get_links_long(long_text_html):
    if long_text_html:
        hyper_links = []
        link = long_text_html.find_all('a')
        for item in link:
            hyper_links.append(item.get('href'))
            item.string = '[链接:'+item.text+']'
        return [url_simplify(item) for item in map(url_filter, hyper_links)]
    return []


def get_weibo_content(feed_content, has_long_text, weibo_id=None):
    """
    获取微博正文，兼容超过140字的情况
    :param feed_content: 单条微博feed_content下的html
    :param has_long_text: 是否有展开全文
    :param weibo_id=None: 微博id，在超过140时必须
    :return 如果不超过140字，返回正文；超过140字返回正文和其中的链接列表
    """
    if feed_content:
        # 先判断有没有展开全文
        # 转发不能超过140字
        content = feed_content.find(
            attrs={'node-type': 'feed_list_content'})
        if has_long_text and weibo_id:
            long_html = get_long_text(weibo_id)
            if long_html:
                html = BeautifulSoup(long_html, 'lxml')
                links = mark_and_get_links_long(html)
                replace_face_with_text_long(html)
                long_content = html.text.strip()
                return links, long_content.replace('\u200b', '').strip()
        else:
            # 如果没有展开全文，返回文本内容
            return content.text.replace('\u200b', '').strip()


def get_repost_weibo(feed_list_item):
    """
    获得转发微博原文
    :param feed_list_item: 单条微博的feed_list_item下的html
    :return: 返回源微博
    """
    handle = feed_list_item.find(attrs={'action-type': "fl_forward"})
    repost_wb_data = WeiboData()
    if handle:
        pattern = re.compile(r'rooturl=(https://weibo.com/\d+/\w+)')
        m = re.search(pattern, str(handle))
        if m:
            ori_url = m.group(1)
            html = get_page(ori_url)
            ori_weibo = get_data(html)
            if len(ori_weibo) == 1:
                repost_wb_data = ori_weibo[0]
    return repost_wb_data


def get_device(feed_content):
    if feed_content:
        wb_from = feed_content.find(attrs={'class': 'WB_from S_txt2'})
        if wb_from:
            f = wb_from.find_all(attrs={'class': 'S_txt2'})
            if len(f) == 2:
                return f[1].text
    else:
        return ""


def get_repost_num(feed_handle):
    """
    获取转发数
    :param feed_handle: 微博html底部的feed_handle的html
    :return: 返回转发数
    """
    try:
        return int(
            feed_handle.find(attrs={'action-type': 'fl_forward'}).find_all('em')[1].text)
    except Exception:
        return 0


def get_comment_num(feed_handle):
    """
    获取评论数
    :param feed_handle: 微博html底部的feed_handle的html
    :return: 返回评论数
    """
    try:
        return int(
            feed_handle.find(attrs={'action-type': 'fl_comment'}).find_all('em')[1].text)
    except Exception:
        return 0


def get_praise_num(feed_handle):
    """
    获取点赞数
    :param feed_handle: 微博html底部的feed_handle的html
    :return: 返回点赞数
    """
    try:
        return int(
            feed_handle.find(attrs={'action-type': 'fl_like'}).find_all('em')[1].text)
    except Exception:
        return 0


def get_weibo_info_detail(each, target_uid=None):
    """
    解析主页单条微博
    :param each:单条微博的 'action-type'='feed_list_item' 的html
    :return: 返回单条微博的信息
    """
    wb_data = WeiboData()
# 获取用户id
    wb_data.uid = get_user_id(each)
    if target_uid and wb_data.uid != target_uid:
        return None
    wb_data.name = get_user_name(each)
# 获取微博id
    wb_data.weibo_id = get_weibo_id(each)
# 获取发布时间
    wb_data.create_time = get_create_time(each)
# 获取微博单条url
    wb_data.weibo_url = get_weibo_url(each)
# 获取单条微博内容html，后面可公用这个bs对象
    feed_content = each.find(attrs={'node-type': 'feed_content'})
    is_repost = feed_content.find(class_='WB_feed_expand')
# 获取微博配图链接
    wb_data.weibo_img = get_weibo_imgs(feed_content, is_repost)
# 获取微博视频链接
    wb_data.weibo_video = get_weibo_clip(feed_content, is_repost)
# 获取正文中的链接
# 在正文中标记出[链接:xxx]
# 如果有展开全文就不在这里获取
# 如果有这个WB_text_opt类就是有展开全文
# TODO 区分正文的展开全文和转发的展开全文
    has_long_text = None
    content = feed_content.find(
        attrs={'node-type': 'feed_list_content'})
    if content:
        has_long_text = content.find(class_='WB_text_opt')
    wb_data.links = mark_and_get_links(feed_content, is_repost, has_long_text)
# 在正文中标记出微博表情[表情:[允悲]]
    replace_face_with_text(feed_content, has_long_text)
# 获取微博正文内容
    res = get_weibo_content(feed_content, has_long_text, wb_data.weibo_id)
    print(wb_data.weibo_url)
    if len and len(res) == 2:
        wb_data.links = res[0]
        wb_data.weibo_cont = res[1]
    else:
        wb_data.weibo_cont = res
# 获取转发的源微博
    if is_repost:
        wb_data.origin_weibo = get_repost_weibo(each)
    else:
        wb_data.origin_weibo = WeiboData()
# 获取发布设备
    wb_data.device = get_device(feed_content)
# 转发，评论，赞
    feed_handle = each.find(attrs={"node-type":"feed_list_options"})
# 获取转发数
    wb_data.repost_num = get_repost_num(feed_handle)
# 获取评论数
    wb_data.comment_num = get_comment_num(feed_handle)
# 获取点赞数
    wb_data.praise_num = get_praise_num(feed_handle)

    return wb_data
