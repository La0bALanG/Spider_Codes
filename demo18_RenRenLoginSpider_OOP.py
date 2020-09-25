# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/24
@file: demo18_RenRenLoginSpider_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:携带cookie登录人人网
"""

import requests
from lxml import etree
from fake_useragent import UserAgent

class RenRenLoginSpider(object):

    '''

    手动登录一次，抓取cookie
    '''

    def __init__(self):
        self.__url = 'http://www.renren.com/975166356/profile'
        self.__headers = {
            'Cookie':'anonymid=kfg4huvsr796dp; depovince=HUN; _r01_=1; JSESSIONID=abcNnIvtJtKrVceQgR9sx; taihe_bi_sdk_uid=2f95a9b367d045acaa5d01f948247f9d; taihe_bi_sdk_session=29ce3835eb24b637346bd140788b3ddf; ick_login=ce3dc1a9-c5ff-4d78-8f9c-fa8d6f878398; t=aedde2d5487361da45e67c6ab2e1ec6d6; societyguester=aedde2d5487361da45e67c6ab2e1ec6d6; id=975166356; xnsid=4250f34e; jebecookies=7cd2ddc3-2852-498d-913e-0127491d7d3b|||||; ver=7.0; loginfrom=null; wp_fold=0',
            'User-Agent':UserAgent().random
        }

    def __get_html(self,url,headers):
        return requests.get(url=url,headers=headers).text

    def __parse_html(self,html):
        dom = etree.HTML(html)
        return dom.xpath('//div[@class="operate_area"]/div[1]/ul/li[1]/span/text()')

    def display(self):
        res = self.__parse_html(self.__get_html(self.__url,self.__headers))
        print(res)

def test():
    RenRenLoginSpider().display()

if __name__ == '__main__':
    test()