# -*- encoding: utf-8 -*-
'''
@File    :   demo04_BaiduImageSpider_OOP.py
@Time    :   2020/09/09 10:01:20
@Author  :   安伟超 
@Version :   1.0
@Contact :   awc19930818@outlook.com
@github  :   https://github.com/La0bALanG
@requirement:
'''

import threading
import requests
from urllib import parse
import re
import os
from lxml import etree


class BaiduImageSpider(object):
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
    
    #单例模式实现：__new__方法
    def __new__(cls, *args, **kwargs):
        if not hasattr(BaiduImageSpider, '_instance'):
            with BaiduImageSpider._instance_lock:
                if not hasattr(BaiduImageSpider, '_instance'):
                    BaiduImageSpider._instance = object.__new__(cls)
        return BaiduImageSpider._instance

    def __init__(self):
        self.__url = 'https://image.baidu.com/search/index?tn=baiduimage&word={}'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }

    #设置只读属性
    @property
    def url(self):
        return self.__url

    @property
    def headers(self):
        return self.__headers

    def __get_html(self,url):
        return requests.get(url=url, headers=self.__headers).text

    def __parse_html(self,html):
        return re.findall('"thumbURL":"(.*?)"', html)

    def __download_image(self,url):
        return requests.get(url=url,headers=self.__headers).content

    def __save_html(self,directory,data):

        # os.path.exists(directory)表示目录存在
        # 如果目录不存在(即先判断是否已存在目标目录)
        if not os.path.exists(directory):
            # 创建空目录并命名
            os.makedirs(directory)
        # 2.循环的对目标图片发起请求获得响应
        for link in data:
            # 请求图片获得响应
            img = self.__download_image(link)
            # 拼接我们想要的图片文件名(包含路径)
            filename = directory + '{}.jpg'.format(link[-24:-15])
            # 写入文件
            with open(filename, 'wb') as f:
                f.write(img)
            f.close()

    def display(self,word):
        directory = '/home/anwc/桌面/{}/'.format(word)
        self.__save_html(directory,self.__parse_html(self.__get_html(self.__url.format(parse.quote(word)))))


def test():
    word = input('请输入明星>>>:')
    BaiduImageSpider.display(word)

if __name__ == '__main__':
    test()
