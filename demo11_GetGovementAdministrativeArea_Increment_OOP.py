# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/14
@file: demo11_GetGovementAdministrativeArea_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:
"""

import requests
import threading
import re
import time
import sys
from lxml import etree
from fake_useragent import UserAgent

"""

目标
1.目标url：http://www.mca.gov.cn/ - 民政数据 - 行政区划代码
   即: http://www.mca.gov.cn/article/sj/xzqh/2019/

2.目标数据: 抓取最新中华人民共和国县以上行政区划代码

实现思路：

1.分析页面及url
    1.请求民政部官网，进入-民政数据-行政区划代码 选项
    2.F12开启控制台，抓手工具抓到：


        2020年7月份县以上行政区划代码
        2020-09-08

        2020年7月份县以下区划变更情况
        2020-09-08

        2020年6月份县以上行政区划代码
        2020-08-31

        2020年6月份县以下区划变更情况
        2020-08-31

        2020年5月份县以上行政区划代码

    3.查看elements：
    <a class="artitlelist" href="/article/sj/xzqh/2020/202009/20200900029334.shtml" target="_blank" title="2020年7月份县以上行政区划代码">2020年7月份县以上行政区划代码</a>
    目标链接在上述a标签的href属性
    但！这是假链接！

    测试：
        现在向该链接(假链接)直接请求行政区划代码详情页，会直接跳转为一个.html页面(真链接)的响应内容，在控制台的response中确实能看到所需数据，但此为.html页面的相应内容，使用python代码直接请求假页面得到的response却根本没有所需数据！

    但是，在假页面的响应内容中，存在如下一段js代码：
    <script>
     window.location.href="http://www.mca.gov.cn//article/sj/xzqh/2020/2020/20200908007001.html";
    </script>

    我们真正想要的真链接其实在这里！

    没错，这也是常见的一种反爬手段，通过伪造url隐藏真实请求的url。

    但，又能奈我何！请求假页面，提取js中的真链接不就行了？

2.拿到真链接。
3.请求真链接的response。
4.解析，持久化存储

实现步骤：
1.请求行政区划代码页面，解析html，得到假url；
2.请求假链接页面response，解析js脚本，获取真实链接；
3.向真实链接请求最终数据
4.解析，持久化存储


"""


class GetGovementAdministrativeAreaSpider(object):
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
        if not hasattr(GetGovementAdministrativeAreaSpider, '_instance'):
            with GetGovementAdministrativeAreaSpider._instance_lock:
                if not hasattr(GetGovementAdministrativeAreaSpider, '_instance'):
                    GetGovementAdministrativeAreaSpider._instance = object.__new__(cls)
        return GetGovementAdministrativeAreaSpider._instance

    def __init__(self):
        self.__url = 'http://www.mca.gov.cn/article/sj/xzqh/2020/'
        self.__headers = {
            'User-Agent': UserAgent().random
        }
        self.__year = ''

    @property
    def url(self):
        return self.__url

    @property
    def headers(self):
        return self.__headers

    @property
    def year(self):
        return self.__year

    def __get_html(self, url, headers):
        return requests.get(url=url, headers=headers)

    # 请求一级页面，解析、构造假链接
    def __get_false_url(self):
        html = self.__get_html(self.__url, self.__headers).text
        dom = etree.HTML(html)
        # 只需要最新的，第一个肯定是最新的
        self.__year = dom.xpath('//li/a[@id="shttnav1"][1]/text()')[0]
        a = dom.xpath('//a[@class="artitlelist"]')[0]
        # 获取节点对象的title属性
        title = a.get('title')
        # 解析所有以“代码”结尾的title
        if title.endswith('代码'):
            return 'http://www.mca.gov.cn' + a.get('href')  # 获取节点对象的href属性

    def __get_true_url(self, false_url):
        # 先获取假链接的响应,然后根据响应获取真链接
        html = self.__get_html(url=false_url, headers=self.__headers).text
        # 利用正则提取真实链接
        return re.findall(r'window.location.href="(.*?)"', html)[0]

    # 请求真实页面，解析数据
    def __parse_html(self, true_url):
        html = self.__get_html(url=true_url, headers=self.__headers).text
        dom = etree.HTML(html)
        tr_lists = dom.xpath('//tr[@height="19"]')
        for tr in tr_lists:
            code = tr.xpath('./td[2]/text()')
            name = tr.xpath('./td[3]/text()')
            if len(code) and len(name) != 0:
                self.__save_html(code[0].strip(), name[0].strip())
            else:
                pass

    def __save_html(self, code, name):
        print('开始写入行政区划代码...')
        filename = self.__year[0:4] + '_Area_code.txt'
        with open(filename, 'a') as f:
            print('写入%s...' % name)
            f.write(code + ':' + name + '\n')
        print('写入完毕.')

    def __Incremental_crawler_simple(self):
        """

        增量爬虫：网站有更新时爬取，无更新时不爬取

        此案例下最简单的增量算法：判断行政区划代码页面第一个是否为当年最新行政区划，是则爬取新代码，否则不爬取
        思路：
            1.解析假url过程中顺带解析“2020年中华人民共和国行政区划代码”该文本
            2.解析出后提取年数信息
            3.time模块获取系统当前时间(获取年份)
            4.判断：解析出的年份与系统年份相符，则未更新，不爬取,否则整体重新爬取行政区划代码

        """

        year = self.__year[0:4]
        os_time = time.strftime('%Y-%m-%d %H:%M:%S')[0:4]
        if year == os_time:
            print('行政区划代码暂无更新，不爬取')
        else:
            update = input('行政区划代码已更新，是否现在立即更新?(y/n):')
            if update == 'y':
                self.__parse_html(self.__get_true_url(self.__get_false_url()))
            else:
                print('暂不更新，增量算法结束，程序执行完毕')
                sys.exit()



    def display(self):
        # self.__parse_html(self.__get_true_url(self.__get_false_url()))
        self.__Incremental_crawler_simple()


def test():
    GetGovementAdministrativeAreaSpider().display()


if __name__ == '__main__':
    test()