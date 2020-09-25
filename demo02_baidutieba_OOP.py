# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/07
@file: demo01_baidutieba_simple.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:1.输入贴吧名称 2.输入起始页 3.输入终止页 4.保存响应的页面内容至txt文档
"""
import threading
from urllib import request, parse

"""
思路：
1.分析页面URL规律
2.构造查询参数
3.发起请求获得响应
4.写入文件

"""
"""
1.分析页面URL规律

打开百度贴吧，随便搜索一个吧，进入，提取出URL：

https://tieba.baidu.com/f?kw=%E9%95%BF%E6%B2%99&ie=utf-8&pn=0
https://tieba.baidu.com/f?kw=%E6%9D%8E%E6%AF%85&ie=utf-8&pn=0
...

查找规律：
    1.kw查询关键字，需要实时传参；
    2.pn页码参数，单位50，代表当前第几页
    3.查询参数因为是汉字，传入时需要先转成urlencode编码

总结URL基本格式：
https://tieba.baidu.com/f?kw={}&ie=utf-8&pn={}

所以，总结思路如下：
    1.构造基本URL格式
    2.构造查询起始页及终止页页码数
    3.构造查询参数及页码参数
    4.字符串拼接，完成最终URL确定格式
"""

"""

确定URL后：
    1.伪造headers
    2.发起正式请求

"""

"""

获得具体响应内容后：
写入文件

"""


class BaiduTiebaSpider(object):
    """

    面向对象思路：
        1.拆分功能细节。整体程序可拆分为:
            1.发请求获得页面
            2.解析页面
            3.持久化存储(写入文件保存)
        2.结合开闭原则，封装功能方法为私有方法，对外提供统一公共接口
        3.采用单例模式：假设本爬虫程序在多个时间、不同情况下多次使用，单例模式实现只创建一个对象，提升性能避免内存占用过高。


    """

    #添加线程锁，避免实际运行过程中受多线程影响
    _instance_lock = threading.Lock()

    def __init__(self):
        self.__url = 'https://tieba.baidu.com/f?kw={}&ie=utf-8&pn={}'

    #单例模式实现：__new__方法

    def __new__(cls, *args, **kwargs):
        if not hasattr(BaiduTiebaSpider, '_instance'):
            with BaiduTiebaSpider._instance_lock:
                if not hasattr(BaiduTiebaSpider, '_instance'):
                    BaiduTiebaSpider._instance = object.__new__(cls)
        return BaiduTiebaSpider._instance

    #设置只读属性，体现封装思想
    @property
    def url(self):
        return self.__url

    def __get_html(self,url):
        # 伪造headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        }
        # 发请求
        # 1.创建请求对象

        reqs = request.Request(url=url, headers=headers)
        # 2.发起正式请求，获得页面响应数据
        return request.urlopen(reqs).read()

    def __parse_html(self):
        pass

    def __save_html(self,filename,html):
        with open(filename,'wb') as f:
            f.write(html)

    def display(self):
        # 构造起始页及终止页
        begin = int(input('请输入起始页：'))
        end = int(input('请输入终止页：'))
        # 查询页码数量：end - begin
        # page = end - begin

        # 构造查询参数并转urlencode编码
        kw = input('请输入您想搜索的贴吧名称>>>:')
        parmas = parse.quote(kw)
        # 依据页码构造最终n个URL
        for page in range(begin, end + 1):
            pn = (page - 1) * 50
            # print(pn)
            finall_url = self.__url.format(parmas, pn)
            html = self.__get_html(finall_url)
            filename = kw + '吧' + '_第%d页.html'%page
            self.__save_html(filename,html)

def test():
    BaiduTiebaSpider().display()

if __name__ == '__main__':
    test()

