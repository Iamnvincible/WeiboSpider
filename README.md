# Weibo Spider

一个针对PC版新浪微博的爬虫, 在 [weibospider](https://github.com/SpiderClub/weibospider)上的二次开发。

## 功能
- 自动登录，保存cookie
- 爬取用户首页全部微博，如果有多页需要在参数中设置
- 针对单条微博链接解析内容
- 给定微博用户id爬取其公开的个人信息

## 使用
在paras.py中设置用户名密码，如果不设置会在运行时提示输入。
运行方式
```
python main.py
```
## 提醒
- 不建议使用自己的微博号爬取大量信息，
- cookie需要每日更新，重新运行一次登录函数即可，登录一次后当天不必再次登录

尚在持续开发中...
