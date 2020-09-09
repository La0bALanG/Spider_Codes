# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/07
@file: demo02_MaoYanMovie_simple.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:1.获取top100榜单页面全部内容；
	2.使用正则匹配出每一条的电影名称，主演，上映时间
	3.将获取的内容写入字典（下一节讲解写入持久化存储）
"""
import threading
import re
import pymysql
import csv
from urllib import request
from time import sleep
from random import randint

"""

数据抓取实现思路：
1.分析URL规律
2.分析页面结构，确定存在所需数据
3.构造headers及最终请求URL
4.发送请求获得相应数据
5.使用正则匹配解析所需数据存入字典

1.分析URL规律

进入猫眼电影网-榜单-top100，随意查看几页，观察其URL规律：
https://maoyan.com/board/4?offset=20
https://maoyan.com/board/4?offset=30
...
https://maoyan.com/board/4?offset=(页数 - 1) * 10

2.分析页面结构，确定存在所需数据
浏览器F12-打开控制台-抓手工具-抓到对应电影内容-查看html信息，如下：

<div class="movie-item-info">
        <p class="name"><a href="/films/4883" title="钢琴家" data-act="boarditem-click" data-val="{movieId:4883}">钢琴家</a></p>
        <p class="star">
                主演：艾德里安·布洛迪,艾米莉娅·福克斯,米哈乌·热布罗夫斯基
        </p>
        <p class="releasetime">上映时间：2002-05-24(法国)</p>    </div>

所需数据存在上部分的响应内容中

3.构造headers及最终请求URL

4.发送请求获得响应数据

5.解析数据
依据上述内容，确定使用正则表达式匹配
匹配思路：
    1.class为name的p标签内部的a标签，其title属性的属性值为电影名称；
    2.class为star的p标签的内容为电影的主演信息；
    3.class为releasetime的p标签的内容为电影的上映时间；

构造正则表达式，匹配以上内容即可：
<div class="movie-item-info">.*?title="(.*?)".*?class="star">(.*?)</p>.*?releasetime">(.*?)</p>

6.数据按照合适形式组织存入字典
"""


class MaoYanMovieSpider(object):
    '''

    面向对象思路：
        1.拆分功能细节。整体程序可拆分为:
            1.发请求获得页面
            2.解析页面
            3.持久化存储(写入文件保存)
        2.结合开闭原则，封装功能方法为私有方法，对外提供统一公共接口
        3.采用单例模式：假设本爬虫程序在多个时间、不同情况下多次使用，单例模式实现只创建一个对象，提升性能避免内存占用过高。

    '''
    # 添加线程锁，避免实际运行过程中受多线程影响

    _instance_lock = threading.Lock()

    def __init__(self):
        self.__url = 'https://maoyan.com/board/4?offset={}'

        # 计数变量
        self.__i = 0

        self.__db = pymysql.connect(
            'localhost', 'root', '185268', 'maoyandb',
            charset='utf8'
        )
        self.__cursor = self.__db.cursor()
        self.all_list = []

    # 单例模式实现：__new__方法
    def __new__(cls, *args, **kwargs):
        if not hasattr(MaoYanMovieSpider, '_instance'):
            with MaoYanMovieSpider._instance_lock:
                if not hasattr(MaoYanMovieSpider, '_instance'):
                    MaoYanMovieSpider._instance = object.__new__(cls)
        return MaoYanMovieSpider._instance

    # 设置只读属性
    @property
    def url(self):
        return self.__url

    @property
    def i(self):
        return self.__i

    @property
    def db(self):
        return self.__db

    @property
    def curosr(self):
        return self.__cursor

    def __get_html(self, url):
        # 伪造headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        }
        # 发请求
        # 1.创建请求对象
        reqs = request.Request(url=url, headers=headers)
        # 2.发起正式请求，获得页面响应数据
        reps = request.urlopen(reqs).read().decode()
        self.__parse_html(reps)

    def __parse_html(self, html):
        # 创建正则对象
        r = re.compile(
            '<div class="movie-item-info">.*?title="(.*?)".*?class="star">(.*?)</p>.*?releasetime">(.*?)</p>', re.S)
        # 正则匹配，查找到的结果存入列表
        find_list = re.findall(r, html)
        self.__save_html(find_list)

    # def __save_html(self,data_list):
    #     dict = {}
    #     # 遍历查询结果集
    #     for item in data_list:
    #         # 每一项内容清洗后存入对应的键名
    #         dict['name'] = item[0].strip()
    #         dict['star'] = item[1].strip()
    #         dict['time'] = item[2].strip()[5:15]
    #         self.__i += 1
    #         print(dict)

    def __save_html(self, data_list):
        for film in data_list:
            self.all_list.append(
                (film[0], film[1].strip(), film[2][5:15])
            )

    def display(self):
        print('爬虫程序开始执行，即将爬取top100榜单信息，每间隔3到5秒继续...')
        for i in range(0, 91, 10):
            url = self.__url.format(i)
            self.__get_html(url)
            # sleep(randint(3,5))
        ins = 'insert into filmtab values(%s,%s,%s)'
        self.__cursor.executemany(ins, self.all_list)
        self.__db.commit()
        self.__cursor.close()
        self.__db.close()
        print('抓取的数据量：%d' % self.__i)


def test():
    MaoYanMovieSpider().display()
    print('爬取完毕...')


if __name__ == '__main__':
    test()







