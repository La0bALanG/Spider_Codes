# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/24
@file: demo18_RenRenLogin_requests_cookie_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:使用requests模块处理
"""

import requests
from lxml import etree
from fake_useragent import UserAgent


class RenRenLoginRequestsSpider(object):
    '''
    原理思路及实现
    # 1. 思路
    requests模块提供了session类,来实现客户端和服务端的会话保持
    # 2. 原理
    1、实例化session对象
    session = requests.session()
    2、让session对象发送get或者post请求
    res = session.post(url=url,data=data,headers=headers)
    res = session.get(url=url,headers=headers)
    # 3. 思路梳理
    浏览器原理: 访问需要登录的页面会带着之前登录过的cookie
    程序原理: 同样带着之前登录的cookie去访问 - 由session对象完成
    1、实例化session对象
    2、登录网站: session对象发送请求,登录对应网站,把cookie保存在session对象中
    3、访问页面: session对象请求需要登录才能访问的页面,session能够自动携带之前的这个cookie,进行请求


    具体步骤

    1、寻找Form表单提交地址 - 寻找登录时POST的地址
    查看网页源码,查看form表单,找action对应的地址: http://www.renren.com/PLogin.do
    2、发送用户名和密码信息到POST的地址
    * 用户名和密码信息以什么方式发送？ -- 字典
    键 ：<input>标签中name的值(email,password)
    值 ：真实的用户名和密码
    post_data = {'email':'','password':''}
    session = requests.session()
    session.post(url=url,data=data)

    '''

    def __init__(self):
        self.__post_url = 'http://www.renren.com/PLogin.do'
        self.__get_url = 'http://www.renren.com/967469305/profile'
        self.__headers = {
            'User-Agent':UserAgent().random
        }
        self.__session = requests.session()


    def __get_html(self):
        form_data = {
            'email':'xx',
            'password':'xx'
        }

        self.__session.post(url=self.__post_url,headers=self.__headers,data=form_data)

        return self.__session.get(url=self.__get_url,headers=self.__headers).text


    def __parse_html(self,html):
        dom = etree.HTML(html)
        return dom.xpath('//div[@class="operate_area"]/div[1]/ul/li[1]/span/text()')

    def display(self):
        res = self.__parse_html(self.__get_html())
        print(res)

def test():
    RenRenLoginRequestsSpider().display()

if __name__ == '__main__':
    test()
