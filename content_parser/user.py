from web import get_page, is_404
from content_parser.user_info import person, public, enterprise
from model import User
import json

BASE_URL = 'http://weibo.com/p/{}{}/info?mod=pedit_more'
NEWCARD_URL = 'https://www.weibo.com/aj/v6/user/newcard?ajwvr=6&name={}&type=1&callback=STK_{}39'
SAMEFOLLOW_URL = 'https://weibo.com/p/100505{}/follow?relate=same_follow&amp;from=page_100505_profile&amp;wvr=6&amp;mod=bothfollow'
# SAMEFOLLOW: only crawl user with 100505 domain


def get_user_info(user_id):
    """
    Get user info according to user id.
    If user domain is 100505,the url is just 100505+userid;
    If user domain is 103505 or 100306, we need to request once more to get his info
    If user type is enterprise or service, we just crawl their home page info
    :param: user id
    :return: user entity
    """
    if not user_id:
        return None

    url = BASE_URL.format('100505', user_id)
    html = get_page(url)

    if not is_404(html):
        domain = public.get_userdomain(html)

        # writers(special users)
        if domain == '103505' or domain == '100306':
            url = BASE_URL.format(domain, user_id)
            html = get_page(url)
            user = get_user_detail(user_id, html)
        # normal users
        elif domain == '100505':
            user = get_user_detail(user_id, html)
        # enterprise or service
        else:
            user = get_enterprise_detail(user_id, html)

        if user is None:
            return None

        #user.name = public.get_username(html)
        user.head_img = public.get_headimg(html)
        #user.verify_type = public.get_verifytype(html)
        #user.verify_info = public.get_verifyreason(html, user.verify_type)
        #user.level = public.get_level(html)

        if user.name:
            print(user.name)
            with open(user.name+'.json', 'w',encoding='utf-8') as file:
                json.dump(user, file, default=lambda obj: obj.__dict__)

            return user
        else:
            return None

    else:
        return None


def get_user_detail(user_id, html):
    user = person.get_detail(html, user_id)
    if user is not None:
        user.uid = user_id
        user.follows_num = person.get_friends(html)
        user.fans_num = person.get_fans(html)
        user.wb_num = person.get_status(html)
    return user


def get_enterprise_detail(user_id, html):
    user = User(user_id)
    user.name = public.get_username(html)
    user.follows_num = enterprise.get_friends(html)
    user.fans_num = enterprise.get_fans(html)
    user.wb_num = enterprise.get_status(html)
    user.description = enterprise.get_description(
        html).encode('gbk', 'ignore').decode('gbk')
    return user
