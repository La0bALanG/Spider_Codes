# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/18
@file: demo16_XiaoMiappsSpider_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:抓取小米应用商店所有应用信息，采用多线程爬取
"""


"""

思路梳理
1.目标:
    百度搜索：小米应用商店 -- 进入官网
    将所有分类下的所有应用的名称及下载链接抓取下来
    
2.思路
    1.分析页面及URL
        1.确认无法直接从页面中获取数据 -- 动态加载
        2.控制台抓包 -- XHR -- response -- 数据存在
        3.确认请求的XHR接口URL:http://app.mi.com/categotyAllListApi?page=0&categoryId=2&pageSize=30
        4.查看并分析查询参数：
            page: 0
            categoryId: 2
            pageSize: 30
        
        多次进入下一页观察查询参数，发现在同一分类下，categoryId及pageSize的参数值为定值，page跟随页数变化
        
        所以可以通过构造page参数实现多页爬取
    
    2.代码实现思路
        1.构造多页请求URL
        2.发请求，请求XHR接口URL，获取response的json数据
        3.解析，写入csv文件
    
    3.多线程思路：
        1、在 __init__(self) 中创建文件对象，多线程操作此对象进行文件写入
            self.f = open('xiaomi.csv','a',newline='')
            self.writer = csv.writer(self.f)
            self.lock = Lock()
        2、每个线程抓取1页数据后将数据进行文件写入，写入文件时需要加锁
            def parse_html(self):
            app_list = []
            for xxx in xxx:
            app_list.append([name,link,typ])
            self.lock.acquire()
            self.wirter.writerows(app_list)
            self.lock.release()
        3、所有数据抓取完成关闭文件
            def main(self):
            self.f.close()

"""


import requests
import time
import csv
import random
import re
from fake_useragent import UserAgent
from lxml import etree
from threading import Lock
from threading import Thread
from queue import Queue



class XiaoMiAppSpider(Thread):
    '''
    多线程爬取小米应用商店案例
    :return:csv文件


    面向对象思路：
        1.拆分功能细节。整体程序可拆分为:
            1.发请求获得页面
            2.解析页面
            3.持久化存储(写入文件保存)
        2.结合开闭原则，封装功能方法为私有方法，对外提供统一公共接口
        3.采用单例模式：假设本爬虫程序在多个时间、不同情况下多次使用，单例模式实现只创建一个对象，提升性能避免内存占用过高。


    '''

    def __init__(self):
        self.__url = 'http://app.mi.com/categotyAllListApi?page={}&categoryId={}&pageSize=30'
        self.__headers = {
            'User-Agent':UserAgent().random
        }

        #存放所有url的队列
        self.__q = Queue()
        self.__i = 0

        #存放所有id类型的空列表
        self.__id_lists = []

        #打开文件
        self.__f = open('xiaomi.csv','a')
        self.__writer = csv.writer(self.__f)

        #创建锁
        self.__lock = Lock()

    def __get_html(self,url):
        return requests.get(url=url,headers=self.__headers)

    #请求官网获取分类id
    def __get_cate_id(self):
        url = 'http://app.mi.com/'
        html = self.__get_html(url).text
        r_list = re.findall('<a href="/category/(.*?)">(.*?)</a>',html)
        for r in r_list:
            #调用url入队列方法，得到的r为id，拼接为完整URL后入队列
            self.__url_in(r)

    #获取页数：通过获取接口的response的json数据中的counts获取页数
    def __get_pages(self,type_id):
        url = self.__url.format(0,type_id)
        count = self.__get_html(url).json()['count']
        return int(count) // 30 + 1

    #根据获取的页数及类型id拼接最终URL并加入URL队列
    def __url_in(self,r):
        pages = self.__get_pages(r[0])
        for page in range(1,pages):
            url = self.__url.format(page,r[0])
            self.__q.put(url)

    def __parse_html(self,html):

        #存放一页的数据 -- 写入csv文件
        app_list = []
        for app in html['data']:
            # 应用名称 + 链接 + 分类
            name = app['displayName']
            link = 'http://app.mi.com/details?id=' + app['packageName']
            typ_name = app['level1CategoryName']
            app_list.append([name,typ_name,link])
            self.__i += 1
        self.__save_csv(app_list)

    #写入csv文件 注意：写入前加锁，写入完毕解锁
    def __save_csv(self,app_list):

        #加锁
        self.__lock.acquire()

        self.__writer.writerows(app_list)

        #解锁
        self.__lock.release()


    #线程事件函数：get() -- 请求 -- 解析 --  保存数据
    def __get_data(self):
        while True:
            #判断队列是否为空
            if not self.__q.empty():
                url = self.__q.get()
                html = self.__get_html(url).json()

                #调用解析数据方法
                self.__parse_html(html)
                pass
            else:
                break

    #线程主函数
    def __main(self):

        #URL入队列
        self.__get_cate_id()

        #创建多线程
        t_list = []

        for i in range(4):
            t = Thread(target=self.__get_data)
            t_list.append(t)
            t.start()

        #回收线程
        for t in t_list:
            t.join()

        #关闭文件
        self.__f.close()
        print('数量:%d'%self.__i)

    #公共接口
    def display(self):
        self.__main()

def test():
    start = time.time()
    XiaoMiAppSpider().display()
    end = time.time()

    print('执行时间：%.2f'%(end - start))

if __name__ == '__main__':
    test()
















