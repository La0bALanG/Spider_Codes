# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/16
@file: demo14_hao123_hotsNews_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:爬取hao123首页推荐的热点新闻
"""

import threading
import requests
import random
import time
from urllib import parse
from lxml import etree
from fake_useragent import UserAgent
from hashlib import md5

"""

var t = 1 === e.page ? e.options.defaultPageSize : e.options.pageSize
                  , o = {
                    pn: e.page,
                    rn: t,
                    ts: +new Date,
                    app_from: "indexnew_feed"
                }

https://www.hao123.com/feedData/data?type=rec&callback=jQuery110103615997331449312_1600222463424&pn=1&rn=10&ts=1600222463554&app_from=indexnew_feed&_=1600222463425
https://www.hao123.com/feedData/data?type=rec&callback=jQuery110103615997331449312_1600222463424&pn=2&rn=10&ts=1600222484611&app_from=indexnew_feed&_=1600222463431
https://www.hao123.com/feedData/data?type=rec&callback=jQuery110103615997331449312_1600222463424&pn=3&rn=10&ts=1600222513497&app_from=indexnew_feed&_=1600222463432

parmas = {
    pn:1,2,3,4,5,
    rn:10,
    ts = str(int(time.time()) * 1000),
    app_from:indexnew_feed,
    _:16002224634 + '25' or 31,32,33
    
}

url = https://www.hao123.com/feedData/data?type=rec&callback=jQuery110103615997331449312_1600222463424



"""

class Hao123HotsNewsSpider(object):
    '''

        面向对象思路：
        1.拆分功能细节。整体程序可拆分为:
            1.发请求获得页面
            2.解析页面
            3.持久化存储(写入文件保存)
        2.结合开闭原则，封装功能方法为私有方法，对外提供统一公共接口
        3.采用单例模式：假设本爬虫程序在多个时间、不同情况下多次使用，单例模式实现只创建一个对象，提升性能避免内存占用过高。

        '''

    _instance_lock = threading.Lock()

    # 单例模式实现：__new__方法
    def __new__(cls, *args, **kwargs):
        if not hasattr(Hao123HotsNewsSpider, '_instance'):
            with Hao123HotsNewsSpider._instance_lock:
                if not hasattr(Hao123HotsNewsSpider, '_instance'):
                    Hao123HotsNewsSpider._instance = object.__new__(cls)
        return Hao123HotsNewsSpider._instance

    def __init__(self):
        self.__url = 'https://www.hao123.com/feedData/data?type=rec&callback=jQuery110103615997331449312_1600222463424'
        self.__headers = {
            'User-Agent':UserAgent().random
        }
        self.__parmas = {
            'pn':'1',
            'rn':'10',
            'ts':str(int(time.time()) * 1000),
            'app_from':'indexnew_feed',
            '_': '1600222463425'
        }

    def __get_data(self):
        return requests.get(url=self.__url,params=self.__parmas,headers=self.__headers).text

    def display(self):
        res = self.__get_data()
        print(res)

Hao123HotsNewsSpider().display()