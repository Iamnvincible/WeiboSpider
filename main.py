from login.login import get_session
from content_parser import get_person_one_full_page, get_user_info
from config import weibo_username, weibo_password

import json
# login and save cookie
if weibo_username == '' or weibo_password == '':
    weibo_username = input("Please input your weibo account name:")
    weibo_password = input("Please input your password:")
session = get_session(weibo_username, weibo_password)
# print(session)

# get user info
#user = get_user_info('2196834344')


# get a specific weibo page and parse it
# from content_parser import get_data
# from web import get_page
# x = get_page('https://weibo.com/1402400261/H8gD5qLuF')
# y = get_data(x)

# get a specific user's full weibo list page
#weibolist = get_person_one_full_page(1, userid='2404981684')
weibolist = get_person_one_full_page(1, name='fly51fly')
with open('weibopage.json', 'w', encoding='utf-8') as file:
    json.dump(weibolist, file, default=lambda obj: obj.__dict__)
