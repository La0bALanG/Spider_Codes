# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/11
@file: demo07_BaiduTiebaSpider_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:
"""

import threading
import requests
import random
import time
from urllib import parse
from lxml import etree
from fake_useragent import UserAgent

"""

设计思路：

目标：爬取贴吧详情页图片及视频

思路：
    1.分析URL规律
        http://tieba.baidu.com/f?kw=??&pn=50
    2.三级爬取
        1.爬取第一级页面：贴吧主页(分页，多页爬取)
        2.爬取第二级页面：帖子详情页，从主页获取帖子链接
        3.爬取第三级：请求图片及视频


xpath表达式
    1、帖子链接xpath
   //div[@class="t_con cleafix"]/div/div/div/a/@href
    
    2、图片链接xpath
   //div[@class="d_post_content j_d_post_content  clearfix"]/img[@class="BDE_Image"]/@src
    
    3、视频链接xpath
   //div[@class="video_src_wrapper"]/embed/@data-video
   # 注意: 此处视频链接前端对响应内容做了处理,需要查看网页源代码来查看，复制HTML代码在线格式化



"""


class BaiduTiebaSpider(object):
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
        if not hasattr(BaiduTiebaSpider, '_instance'):
            with BaiduTiebaSpider._instance_lock:
                if not hasattr(BaiduTiebaSpider, '_instance'):
                    BaiduTiebaSpider._instance = object.__new__(cls)
        return BaiduTiebaSpider._instance

    def __init__(self):
        self.__url = 'http://tieba.baidu.com/f?kw={}&pn={}'
        self.__headers = {
            'User-Agent':UserAgent().random
        }

    def __get_html(self,url,headers):
        return requests.get(url=url,headers=headers).content.decode('utf-8','ignore')

    def __xpath_function(self,html,xpath_expression):
        dom = etree.HTML(html)
        return dom.xpath(xpath_expression)

    def __parse_html(self,url):
        html = self.__get_html(url)
        link_lists = self.__xpath_function(html,'//div[@class="t_con cleafix"]/div/div/div/a/@href')
        for link in link_lists:
            tie_url = 'https://tieba.baidu.com' + link
            self.__get_image(tie_url)
            time.sleep(random.randint(0,2))

    def __get_image(self,url):
        html = self.__get_html(url)
        img_lists = self.__xpath_function(html,'//div[@class="d_post_content j_d_post_content  clearfix"]/img[@class="BDE_Image"]/@src')
        for img in img_lists:
            img_bytes = self.__get_html(img).encode()
            self.__save_img(img_bytes,img)

    def __save_img(self,data,img):
        filename = img[-10:]
        with open(filename,'wb') as f:
            f.write(data)
        print('%s下载成功'%img)


    def display(self):
        name = input('请输入贴吧名称：')
        begin = int(input('请输入起始页：'))
        end = int(input('请输入终止页：'))
        kw = parse.quote(name)
        for page in range(begin,end + 1):
            pn = (page - 1) * 50
            url = self.__url.format(kw,pn)
            self.__parse_html(url)

def test():
    res = BaiduTiebaSpider()
    res.display()

if __name__ == '__main__':
    test()