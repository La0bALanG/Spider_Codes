# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/09
@file: demo05_MaoYanMovie_xpath_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:
"""

import threading
import requests
from lxml import etree
from fake_useragent import UserAgent


"""

分析
1、基准xpath: 匹配所有电影信息的节点对象列表
    //dl[@class="board-wrapper"]/dd
    
2、遍历对象列表，依次获取每个电影信息
   for dd in dd_list:
	   电影名称 ：.//p[@class="name"]/a/@title
	   电影主演 ：.//p[@class="star"]/text()
	   上映时间 ：.//p[@class="releasetime"]/text()

"""


class MaoYanMovieXpathSpider(object):
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
        if not hasattr(MaoYanMovieXpathSpider, '_instance'):
            with MaoYanMovieXpathSpider._instance_lock:
                if not hasattr(MaoYanMovieXpathSpider, '_instance'):
                    MaoYanMovieXpathSpider._instance = object.__new__(cls)
        return MaoYanMovieXpathSpider._instance

    def __init__(self):
        self.__url = 'https://maoyan.com/board/4?offset={}'
        self.__headers = {
            'User-Agent':UserAgent().random
        }

    #设置只读属性
    @property
    def url(self):
        return self.__url

    @property
    def headers(self):
        return self.__headers

    def __get_html(self,url):
        return requests.get(url=url,headers=self.__headers).text

    def __parse_html(self,html):
        dict = {}
        dom = etree.HTML(html)
        dd_list = dom.xpath('//dl[@class="board-wrapper"]/dd')
        for item in dd_list:
            dict['name'] = item.xpath('.//p[@class="name"]/a/@title')
            dict['star'] = item.xpath('.//p[@class="star"]/text()')
            dict['time'] = item.xpath('.//p[@class="releasetime"]/text()')
            print(dict)

    def display(self):
        for offset in range(0,91,10):
            url = self.__url.format(offset)
            self.__parse_html(self.__get_html(url))

def test():
    MaoYanMovieXpathSpider().display()

if __name__ == '__main__':
    test()