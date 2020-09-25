# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/22
@file: demo17_TencentJobSpider_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:
"""


import requests
import time
import json
import random
from openpyxl import Workbook
from fake_useragent import UserAgent
from urllib import parse



class TencentJobSpider(object):



    def __init__(self):

        #定义一二级页面初始URL
        self.__first_url = 'https://careers.tencent.com/tencentcareer/api/post/Query?timestamp={}&countryId=&cityId=&bgIds=&productId=&categoryId=&parentCategoryId=&attrId=&keyword={}&pageIndex={}&pageSize=10&language=zh-cn&area=cn'
        self.__second_url = 'https://careers.tencent.com/tencentcareer/api/post/ByPostId?timestamp={}&postId={}&language=zh-cn'

        #定义headers
        self.__headers = {
            'User-Agent':UserAgent().random
        }

        #创建excel写入实例，并新建sheet
        self.__wb = Workbook()
        self.__ws = self.__wb.create_sheet('job_info')


        #计数变量
        self.__i = 0


    def __get_html(self,url,headers):
        return requests.get(url=url,headers=headers)


    def __url_in(self):
        keyword = input('请输入职位关键字：')
        keyword = parse.quote(keyword)
        lts = str(int(time.time()) * 1000)
        total = self.__get_total(keyword)
        print('一共检索到%d页招聘信息;'%total)
        for page in range(1,total+1):
            f_url = self.__first_url.format(lts, keyword, page)
            self.__parse_first_page(f_url)

    def __get_total(self,keyword):
        url = self.__first_url.format(str(int(time.time()) * 1000),keyword,1)
        num = int(self.__get_html(url,self.__headers).json()['Data']['Count'])
        if num % 10 == 0:
            total = num // 10
        else:
            total = num // 10 + 1
        return total

    def __parse_first_page(self,url):
        html = json.loads(self.__get_html(url,self.__headers).text)
        lts = str(int(time.time()) * 1000)
        for job in html['Data']['Posts']:
            post_id = job['PostId']
            s_url = self.__second_url.format(lts,post_id)
            self.__parse_second_page(s_url)


    def __parse_second_page(self,url):

        html = json.loads(self.__get_html(url,self.__headers).text)
        # print(html)

        lists = []

        lists.append(html['Data']['RecruitPostName'])
        lists.append(html['Data']['Responsibility'])
        lists.append(html['Data']['Requirement'])

        print('抓取一条信息：%s,开始写入excel...'%lists)

        self.__ws.append(lists)
        self.__i += 1
        print('写入完毕，抓取下一条')

    def display(self):
        self.__url_in()

        print('爬取总数：%d'%self.__i)
        print('爬取完毕，保存excel表格...')
        self.__wb.save('TencentGetJob.xlsx')
        print('保存成功！')

def test():
    TencentJobSpider().display()

if __name__ == '__main__':
    test()
