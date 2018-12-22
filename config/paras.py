# coding=utf-8
time_out = 200                   # timeout for crawling and storing user info
min_crawl_interal = 10           # min interal of http request
max_crawl_interal = 20           # max interal of http request
excp_interal = 5*60              # time for sleeping when crawling raises exceptions

# TODO set a default value for max_value of crawling
max_search_page = 50            # max search page for crawling
max_home_page = 50              # max user home page for crawling
max_comment_page = 2000         # max comment page for crawling
max_repost_page = 2000          # max repost page for crawling
max_dialogue_page = 2000        # max dialogue page for crawling
max_retries = 5                 # retry times for crawling

weibo_username = ''
weibo_password = ''
ORIGIN = 'http'
PROTOCOL = 'https'
ROOT_URL = 'weibo.com'

# only crawl weibo(bowen) after
# only affect to home crawler
time_after = '1970-01-01 08:00:00'

# whether account follows the uid below
# if yes rows in wbuser will have 1 at isFan column
samefollow_uid = ''

# The value of running_mode can be normal or quick.
# In normal mode, it will be more stable, while in quick mode, the crawling speed will
# be much faster, and the weibo account almostly will be banned
running_mode = 'normal'

# The value of crawling mode can be accurate or normal
# In normal mode, the spider won't crawl the weibo content of "展开全文" when execute home crawl tasks or search crawl
# tasks, so the speed will be much quicker.
# In accurate mode,the spider will crawl the info of "展开全文",which will be slower, but more details will be given.
crawling_mode = 'normal'


# the expire time(hours) of each weibo cookies
cookie_expire_time = 23

# 1 for allow download images, otherwise set it to 0
images_allow = 1

# the default image path is '${user.home}/weibospider/images'
# if you want to change another directory for download image, just set the path below
images_path = ''

# the value can be large or thumbnail
# in large type, you will download the large image
# in thumbnail type, you will download the thumbnail image
image_type = 'large'
