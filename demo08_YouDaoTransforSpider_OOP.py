# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/11
@file: demo08_YouDaoTransforSpider_OOP.py.py
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
from hashlib import md5

"""

实现目标：
    破解有道翻译接口，抓取对应翻译结果

目标展示：
    输入原文：你好
    翻译结果：hello

实现步骤：
    1、浏览器F12开启网络抓包,Network-All,页面翻译单词后找Form表单数据
    2、在页面中多翻译几个单词，观察Form表单数据变化（有数据是加密字符串）
    3、刷新有道翻译页面，抓取并分析JS代码（本地JS加密）
    4、找到JS加密算法，用Python按同样方式加密生成加密数据
    5、将Form表单数据处理为字典，通过requests.post()的data参数发送
    
实现思路：
    1.F12抓包，一次翻译请求后查看对应form表单数据(有道翻译请求为异步AJAX加载，直接在XHR内部查看即可)
    查找到的form表单数据如下：
    
        i: 电话
        from: AUTO
        to: AUTO
        smartresult: dict
        client: fanyideskweb
        salt: 15997921298483
        sign: 8d61b0f42e54f5901012f69540fc918b
        lts: 1599792129848
        bv: e915c77f633538e8cf44c657fe201ebb
        doctype: json
        version: 2.1
        keyfrom: fanyi.web
        action: FY_BY_REALTlME

    在页面中多翻译几个单词，查看form表单的数据变化：
    
        i: 朋友
        from: AUTO
        to: AUTO
        smartresult: dict
        client: fanyideskweb
        salt: 15997929113988
        sign: 04852e09170834a641b8ab0acff7b6ef
        lts: 1599792911398
        bv: e915c77f633538e8cf44c657fe201ebb
        doctype: json
        version: 2.1
        keyfrom: fanyi.web
        action: FY_BY_REALTlME

    观察发现：不同翻译结果的情况下发生改变的参数为：
    
        salt: 15997921298483
        sign: 8d61b0f42e54f5901012f69540fc918b
        lts: 1599792129848
        bv: e915c77f633538e8cf44c657fe201ebb
        
    3.破解加密：一般为本地js文件加密，刷新一下页面，找到js文件并分析js代码
    如何查找对应的js文件：
        # 方法1
        Network - JS选项 - 搜索关键词salt
        # 方法2
        控制台右上角 - Search - 搜索salt - 查看文件 - 格式化输出
        # 最终找到相关JS文件 : fanyi.min.js
        
    按照如上方法，搜索关键词，例如搜索salt，左侧列出salt关键词存在的js文件为fanyi.min.js
    进入该js文件，继续搜索salt关键词，对多个关键词结果进行筛选，最终在如下js代码中发现关键信息：
    
     var r = function(e) {
        var t = n.md5(navigator.appVersion)
          , r = "" + (new Date).getTime()
          , i = r + parseInt(10 * Math.random(), 10);
        return {
            ts: r,
            bv: t,
            salt: i,
            sign: n.md5("fanyideskweb" + e + i + "]BjuETDhU)zqSxf-=B#7m")
        }
    };
    
    分析如上代码得知：
        1.ts为13位时间戳，字符串类型，对应data中的lts参数
            js代码实现："" + (new Date).getTime()
            python代码实现：str(int(time.time()) * 1000)
        2.salt:ts + 某一随机数，其随机数规律如下：
            js代码实现：r(ts) + parseInt(10 * Math.random(), 10)
            python代码实现：ts+str(random.randint(0,9))
            
        3.sign（设置断点调试，来查看 e 的值，发现 e 为要翻译的单词）
        js代码实现: n.md5("fanyideskweb" + e + salt + "n%A-rKaT5fb[Gy?;N5@Tj")
        python实现:
            from hashlib import md5
            string = "fanyideskweb" + word + salt + "n%A-rKaT5fb[Gy?;N5@Tj"
            s = md5()
            s.update(string.encode())
            sign = s.hexdigest()
"""



class YouDaoTransforSpider(object):
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
        if not hasattr(YouDaoTransforSpider, '_instance'):
            with YouDaoTransforSpider._instance_lock:
                if not hasattr(YouDaoTransforSpider, '_instance'):
                    YouDaoTransforSpider._instance = object.__new__(cls)
        return YouDaoTransforSpider._instance

    def __init__(self):
        self.__url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        self.__headers = {
            'Cookie':'OUTFOX_SEARCH_USER_ID=1559141275@10.169.0.83; JSESSIONID=aaaUEr86rzfeo7xp8b7rx; OUTFOX_SEARCH_USER_ID_NCOO=1009771993.8014448; ___rl__test__cookies=1599793115062',
            'Referer': 'http: // fanyi.youdao.com /',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        }

    def __get_salt_sign_ts(self,word):

        #ts
        ts = str(int(time.time()) * 1000)

        #salt
        salt = ts + str(random.randint(0,9))

        #sign
        string = "fanyideskweb" + word + salt + "]BjuETDhU)zqSxf-=B#7m"
        s = md5()
        s.update(string.encode())
        sign = s.hexdigest()

        return salt,sign,ts

    def __get_data(self,word):
        salt,sign,ts = self.__get_salt_sign_ts(word)

        #设置提交数据格式
        data = {
            'i': word,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salt,
            'sign': sign,
            'lts': ts,
            'bv': 'e915c77f633538e8cf44c657fe201ebb',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action':'FY_BY_REALTlME'
        }

        return requests.post(url=self.__url,data=data,headers=self.__headers).json()['translateResult'][0][0]['tgt']

    def display(self):
        word = input('请输入要翻译的单词：')
        tre_word = self.__get_data(word)
        print('翻译后的结果：%s'%tre_word)
def test():
    YouDaoTransforSpider().display()

if __name__ == '__main__':
    test()

