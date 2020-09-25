# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/11
@file: demo09_re_headers_and_formData.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:使用正则表达式预处理headers及form表单数据
"""

import re

class demoSpider(object):

    def __init__(self):
        self.__headers = """
Accept: application/json, text/javascript, */*; q=0.01
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Content-Length: 248
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Cookie: OUTFOX_SEARCH_USER_ID=1559141275@10.169.0.83; JSESSIONID=aaaUEr86rzfeo7xp8b7rx; OUTFOX_SEARCH_USER_ID_NCOO=1009771993.8014448; ___rl__test__cookies=1599804152408
Host: fanyi.youdao.com
Origin: http://fanyi.youdao.com
Referer: http://fanyi.youdao.com/
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36
X-Requested-With: XMLHttpRequest
"""
        self.__formData = """
i: 朋友
from: zh-CHS
to: en
smartresult: dict
client: fanyideskweb
salt: 15998041524052
sign: bf3ecd8f4c8a282ed79468f49aeb69fd
lts: 1599804152405
bv: e915c77f633538e8cf44c657fe201ebb
doctype: json
version: 2.1
keyfrom: fanyi.web
action: lan-select
        """

    def re_parse(self,str_data):
        dict = {}
        for x,y in re.findall('(.*):(.*)',str_data):
            dict[x] = y.strip()
        return dict

    def display(self):
        headers = self.re_parse(self.__headers)
        form_data = self.re_parse(self.__formData)
        print(headers)
        print(form_data)

demoSpider().display()