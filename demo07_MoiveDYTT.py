# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/07
@file: demo03_MoiveDYTT.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:把电影天堂数据存入MySQL数据库
"""

# import pymysql
import threading
import pymysql
import re
import requests
from selenium import webdriver
from lxml import etree


"""

需求：把电影天堂数据存入MySQL数据库 - 增量爬取
地址:
    一级页面：
        https://www.dytt8.net/html/gndy/index.html
    二级页面：
        https://www.dytt8.net/html/gndy/china/index.html
        https://www.dytt8.net/html/gndy/rihan/index.html
        https://www.dytt8.net/html/gndy/oumei/index.html

    二级页面分页规律：
        国产电影：
            https://www.dytt8.net/html/gndy/china/list_4_1.html
            https://www.dytt8.net/html/gndy/china/list_4_2.html
            https://www.dytt8.net/html/gndy/china/list_4_3.html
            ...
            https://www.dytt8.net/html/gndy/china/list_4_n.html
        欧美电影：
            https://www.dytt8.net/html/gndy/oumei/list_7_1.html
            https://www.dytt8.net/html/gndy/oumei/list_7_2.html
            https://www.dytt8.net/html/gndy/oumei/list_7_3.html
            https://www.dytt8.net/html/gndy/oumei/list_7_4.html
            ...
            https://www.dytt8.net/html/gndy/oumei/list_7_n.html
        日韩电影：
            https://www.dytt8.net/html/gndy/rihan/list_6_1.html
            https://www.dytt8.net/html/gndy/rihan/list_6_2.html
            https://www.dytt8.net/html/gndy/rihan/list_6_3.html
            ...
            https://www.dytt8.net/html/gndy/rihan/list_6_n.html

    总结：
        china -- 4
        rihan -- 6
        oumei -- 7
        
        https://www.dytt8.net/html/gndy/{}/list_{}_n.html
        {
            'china':'4',
            'rihan':'6',
            'oumei':'7'
        }

目标:电影名称、下载链接
分析：
*********一级页面所需数据***********
        1、提取二级页面URL
        2、分类电影详情页链接
        
*********二级页面所需数据***********
        1、提取三级页面URL
  		3、单个电影详情页链接
*********三级页面所需数据***********
        1、电影名称
  		3、对应的磁力下载链接

实现步骤:
1、发请求，拿数据
2、写xpath表达式依次解析数据
    一级页面：
        电影地区：'//div[@class="title_all"]/p/strong/text()'
        二级页面URL：'//div[@class="title_all"]/p/em/a/@href'
    二级页面：
        电影详情页URL：'//table/tbody/tr[2]/td[2]/b/a[2]/@href'
    三级页面：        
        电影名称：'//div[@class="title_all"]/h1/font/text()'
        磁力链接：'//div[@id="Zoom"]/span[@style="FONT-SIZE: 12px"]/a/@href'
3.数据持久化存储

数据库建库建表：

create database filmskydb charset utf8;
use filmskydb;
create table request_finger(
finger char(32)
)charset=utf8;
create table filmtab(
name varchar(200),
download varchar(500)
)charset=utf8;

"""

class MovieDYTTSpider(object):
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

        #初始页面url，可获取二级页面url
        self.__init_url = 'https://www.dytt8.net/html/gndy/index.html'

        #二级页面url，可获取电影详情页url
        self.__second_url = ''

        #三级页面：电影详情页url，获取最终目标数据
        self.__movie_url = ''

        #二级页面url所需格式参数，用于拼接最终二级url
        self.__i = [4,6,7]

        #伪造请求头
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        }

        #使用webdriver模拟浏览器操作

        #模拟chrome浏览器操作，不打开预览页面
        chromeoptions = webdriver.ChromeOptions()
        chromeoptions.add_argument('--headless','')

        #创建webdriver对象
        self.__driver = webdriver.Chrome(chrome_options=chromeoptions)

        #建立mysql链接
        self.__db = pymysql.connect(
            'localhost', 'root', '185268', 'filmskydb',
            charset='utf8'
        )
        self.__cursor = self.__db.cursor()

    #单例模式实现
    def __new__(cls, *args, **kwargs):
        if not hasattr(MovieDYTTSpider, '_instance'):
            with MovieDYTTSpider._instance_lock:
                if not hasattr(MovieDYTTSpider, '_instance'):
                    MovieDYTTSpider._instance = object.__new__(cls)
        return MovieDYTTSpider._instance

    #只读属性
    @property
    def init_url(self):
        return self.__init_url

    @property
    def second_url(self):
        return self.__second_url

    @property
    def movie_url(self):
        return self.__movie_url

    @property
    def i(self):
        return self.__i

    @property
    def headers(self):
        return self.__headers

    @property
    def driver(self):
        return self.__driver

    @property
    def db(self):
        return self.__db

    @property
    def cursor(self):
        return self.__cursor


    #-----功能代码实现--------

    #请求页面：私有方法，负责调用chrome对象获取页面并返回页面资源
    def __get_html(self,url):
        self.__driver.get(url)
        reps = self.__driver.page_source
        # print(type(reps))
        return reps

    #解析一级页面
    def __parse_first_html(self,html):
        #xpath解析
        dom = etree.HTML(html)
        movie_area = dom.xpath('//div[@class="title_all"]/p/strong/text()')
        second_html_href = dom.xpath('//div[@class="title_all"]/p/em/a/@href')
        return [movie_area.pop(),second_html_href.pop()]

    #解析二级页面
    def __parse_second_html(self,html):
        dom = etree.HTML(html)
        movie_list = dom.xpath('//table/tbody/tr[2]/td[2]/b/a[2]/@href')
        return movie_list

    #解析三级页面
    def __parse_third_html(self,html):
        dom = etree.HTML(html)
        movie_name = dom.xpath('//div[@class="title_all"]/h1/font/text()')
        movie_marget = dom.xpath('//div[@id="Zoom"]/span[@style="FONT-SIZE: 12px"]/a/@href')
        return zip(movie_name,movie_marget)

    #写入数据库：持久化存储
    def __save_html(self,name,marget):
        ins = 'insert into filmtab values(%s,%s)'
        self.__cursor.execute(ins,name,marget)
        self.__db.commit()

    #公共接口：功能整合，类外返回数据
    def display(self,num):

        #1.请求一级页面并解析数据，获得二级页面所需URL(部分，还要进行拼接)
        res = self.__parse_first_html(self.__get_html(self.__init_url))

        #遍历一级页面响应数据和url所需参数的参数列表
        for (sec,i) in zip(res[1],self.__i):

            #模拟循环多页进行爬取，num表示页数
            for j in range(1, num + 1):
                #拼接出所需的二级页面的URL
                self.__second_url = 'https://www.dytt8.net' + sec[0:-10] + 'list_{}_{}.html'.format(i,j)
                #2.请求2级页面并解析数据，获得电影详情页最终URL(部分，还要进行拼接)
                sec_data = self.__parse_second_html(self.__get_html(self.__second_url))
                #遍历二级页面响应内容
                for m_url in sec_data:
                    #3.拼接电影详情页最终URL
                    self.__movie_url = 'https://www.dytt8.net' + m_url
                    #请求最终电影详情页，获得电影名称及其对应的迅雷下载磁力链接码
                    movie_data = self.__parse_third_html(self.__get_html(self.__movie_url))
                    #遍历电影名称及磁力链接
                    for (name,marget) in movie_data:
                        #调用save方法将数据写入数据库
                        self.__save_html(name,marget)

def test():
    num = int(input('您想爬多少页的内容，请输入>>>:'))
    MovieDYTTSpider().display(num)

if __name__ == '__main__':
    test()

    

