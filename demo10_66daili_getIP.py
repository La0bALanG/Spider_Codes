# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/12
@file: demo10_xicidaili_getIP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:爬取66代理所有可用代理IP，存入文件，作为个人IP代理池
"""

import threading
import requests
import time
import random
from lxml import etree
from fake_useragent import UserAgent

class GetXiCiDaiLiIPSpider(object):
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
        if not hasattr(GetXiCiDaiLiIPSpider, '_instance'):
            with GetXiCiDaiLiIPSpider._instance_lock:
                if not hasattr(GetXiCiDaiLiIPSpider, '_instance'):
                    GetXiCiDaiLiIPSpider._instance = object.__new__(cls)
        return GetXiCiDaiLiIPSpider._instance

    def __init__(self):
        self.__url = 'https://www.kuaidaili.com/free/inha/{}/'
        self.__headers = {
            'User-Agent':UserAgent().random
        }

    def __get_html(self,url,headers):
        return requests.get(url=url,headers=headers).text

    def __parse_html(self,html):
        dom = etree.HTML(html)
        tr_lists = dom.xpath('//table/tbody/tr')
        #第一个tr不是ip及端口号信息，跳过第1个，从第2个tr开始提取
        for tr in tr_lists:
            ip = tr.xpath('./td[1]/text()')[0]
            port = tr.xpath('./td[2]/text()')[0]
            self.__test_IP(ip,port)

    def __test_IP(self,ip,port):
        proxies = {
            'http': 'http://{}:{}'.format(ip, port),
            'https': 'https://{}:{}'.format(ip, port),
        }
        test_url = 'https://www.hao123.com/'
        try:
            res = requests.get(url=test_url,proxies=proxies,timeout=8)
            if res.status_code == 200:
                print('代理ip:%s:%s测试完毕，success,采用，即将写入代理池文件'%(ip,port))
                with open('proxies.txt','a') as f:
                    print('写入代理ip...')
                    f.write(ip + ':' + port + '\n')
                    print('写入完成，测试下一条代理ip...')
        except Exception as e:
            print('代理ip:%s:%s测试完毕，faild,不采用，测试下一条代理ip...'%(ip,port))
    def display(self):
        begin = int(input('请输入开始页数：'))
        end = int(input('请输入结束页数：'))
        for i in range(begin,end + 1):
            print('开始爬取第%d页代理ip...'%i)
            url = self.__url.format(i)
            self.__parse_html(self.__get_html(url,self.__headers))
            time.sleep(random.randint(0,3))

def test():
    GetXiCiDaiLiIPSpider().display()

if __name__ == '__main__':
    test()