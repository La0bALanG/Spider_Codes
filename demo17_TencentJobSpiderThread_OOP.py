# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/19
@file: demo17_TencentJobSpider_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:多线程抓取腾讯招聘岗位信息存入excel表格
"""

import requests
import time
import json
import random
from openpyxl import Workbook
from fake_useragent import UserAgent
from queue import Queue
from threading import Thread,Lock
from urllib import parse

"""

思路

目标：百度搜索腾讯招聘 - 查看工作岗位，获取：职位名称、工作职责、岗位要求

1.页面及URL分析：
    1.F12控制台查看网页，发现为动态加载数据
    2.F12控制台对XHR抓包，得一级页面json数据地址URL：
        'https://careers.tencent.com/tencentcareer/api/post/Query?timestamp={}&countryId=&cityId=&bgIds=&productId=&categoryId=&parentCategoryId=&attrId=&keyword={}&pageIndex={}&pageSize=10&language=zh-cn&area=cn'Id=&keyword=&pageIndex={}&pageSize=10&language=zh-cn&area=cn
    3.二级页面json数据地址URL:
        'https://careers.tencent.com/tencentcareer/api/post/ByPostId?timestamp={}&postId={}&language=zh-cn'{}&language=zh-cn

2.整体思路
    1.请求接口获取json数据
    2.解析数据拼接URL存入队列
        1.一级页面URL入first队列，对应线程事件处理函数1
        2.二级页面URL入second队列，对应线程事件处理函数2
    3.多个线程从URL队列中读取并请求最终数据
    4.多线程写入excel文件，注意加锁
"""

class SpiderThread(Thread):

    def __init__(self,target=None):
        super().__init__()
        self.target = target

    def run(self):
        self.target()

class TencentJobSpider(object):

    '''



    '''

    def __init__(self):

        #定义一二级页面初始URL
        self.__first_url = 'https://careers.tencent.com/tencentcareer/api/post/Query?timestamp={}&countryId=&cityId=&bgIds=&productId=&categoryId=&parentCategoryId=&attrId=&keyword={}&pageIndex={}&pageSize=10&language=zh-cn&area=cn'
        self.__second_url = 'https://careers.tencent.com/tencentcareer/api/post/ByPostId?timestamp={}&postId={}&language=zh-cn'

        #定义headers
        self.__headers = {
            'User-Agent':UserAgent().random
        }
        #定义一级二级页面对应的URL队列
        self.__first_q = Queue()
        self.__second_q = Queue()

        #创建excel写入实例，并新建sheet
        self.__wb = Workbook()
        self.__ws = self.__wb.create_sheet('job_info')

        #创建锁
        self.__lock = Lock()

        #计数变量
        self.__i = 0

    def __get_html(self,url,headers):
        return requests.get(url=url,headers=headers)

    def __parse_first_page(self):
        '''
        解析一级页面
        目的：拿postid参数拼接二级页面URL
        对应线程事件处理函数1

        :return: 二级页面URL
        '''
        while True:
            if not self.__first_q.empty():
                url = self.__first_q.get()
                html = json.loads(self.__get_html(url,self.__headers).text)
                lts = str(int(time.time()) * 1000)
                for job in html['Data']['Posts']:
                    post_id = job['PostId']
                    s_url = self.__second_url.format(lts,post_id)
                    self.__second_q.put(s_url)
            else:
                break

    def __parse_second_page(self):
        '''
        解析二级页面
        目的：拿最终数据,写入文件
        :return: None
        '''
        while True:
            try:
                url = self.__second_q.get()
                html = json.loads(self.__get_html(url,self.__headers).text)
                # print(html)

                lists = []

                lists.append(html['Data']['RecruitPostName'])
                lists.append(html['Data']['Responsibility'])
                lists.append(html['Data']['Requirement'])

                print('抓取一条信息：%s,开始写入excel...'%lists)

                self.__lock.acquire()
                self.__ws.append(lists)
                self.__i += 1
                print('写入完毕，抓取下一条')
                self.__lock.release()

            except Exception as e:
                break

    def __url_in(self):
        keyword = input('请输入职位关键字：')
        keyword = parse.quote(keyword)
        lts = str(int(time.time()) * 1000)
        total = self.__get_total(keyword)
        print('一共检索到%d页招聘信息;'%total)
        for page in range(1,total+1):
            f_url = self.__first_url.format(lts, keyword, page)
            self.__first_q.put(f_url)

    def __get_total(self,keyword):
        url = self.__first_url.format(str(int(time.time()) * 1000),keyword,1)
        num = int(self.__get_html(url,self.__headers).json()['Data']['Count'])
        if num % 10 == 0:
            total = num // 10
        else:
            total = num // 10 + 1
        return total

    def __event_first(self):
        self.__parse_first_page()

    def __event_second(self):
        self.__parse_second_page()

    def display(self):
        self.__url_in()
        begin = time.time()
        print('即将开始多线程爬取...')
        t1_list = []
        t2_list = []
        for i in range(5):
            t = SpiderThread(target=self.__event_first)
            t1_list.append(t)
            t.start()
            print('一级页面线程T%d开始执行'%i)

        for j in range(5):
            t = SpiderThread(target=self.__event_second)
            t2_list.append(t)
            t.start()
            print('二级页面线程T%d开始执行'%j)

        for t in t1_list:
            t.join()

        for t in t2_list:
            t.join()

        print('爬取总数：%d'%self.__i)
        print('爬取完毕，保存excel表格...')
        end = time.time()
        self.__wb.save('TencentGetJob.xlsx')
        print('保存成功！')
        print('共计用时：%.2f'%(end - begin))



def test():
    TencentJobSpider().display()

if __name__ == '__main__':
    test()