# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/15
@file: demo12_DouBanMovieComments_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:豆瓣电影评分数据抓取
"""

import requests
import threading
import re
import time
import random
from fake_useragent import UserAgent


"""

实现思路

思路：
1.目标数据
    地址: 豆瓣电影 - 排行榜 - 剧情
    目标: 电影名称、电影评分
    
2.F12控制台抓包分析
    1.先检索我们所需的第一目标数据：电影名称、电影评分
        F12 -- network -- XHR -- 鼠标滚动不断刷新页面 -- 查看左侧AJAX异步加载项 -- preview 
        
        分析多次刷新规律得知该AJAX接口请求的路径如下：
        https://movie.douban.com/j/chart/top_list?type=11&interval_id=100%3A90&action=&start=0&limit=20
        由此得到基准URL格式：
        https://movie.douban.com/j/chart/top_list?
        后续的参数在请求时通过parmas参数拼接传入
        
        得到的一次AJAX请求的response结果如下：
        [
            {"rating":["9.4","50"],"rank":21,"cover_url":"https://img2.doubanio.com\/view\/photo\/s_ratio_poster\/public\/p2329626263.jpg","is_playable":false,"id":"20326557","types":["剧情","爱情","音乐"],"regions":["法国"],"title":"巴黎圣母院","url":"https:\/\/movie.douban.com\/subject\/20326557\/","release_date":"1998","actor_count":7,"vote_count":9691,"score":"9.4","actors":["海伦娜·赛加拉","加劳","丹尼尔·拉沃伊","布鲁诺·佩尔蒂埃","帕特里克·费欧里","拉克·默维尔","朱丽叶·泽纳缇"],"is_watched":false},
            {"rating":["9.4","50"],"rank":22,"cover_url":"https://img9.doubanio.com\/view\/photo\/s_ratio_poster\/public\/p2224933614.jpg","is_playable":false,"id":"25928148","types":["剧情","爱情","歌舞"],"regions":["法国"],"title":"罗密欧与朱丽叶","url":"https:\/\/movie.douban.com\/subject\/25928148\/","release_date":"2002-02-06","actor_count":4,"vote_count":4782,"score":"9.4","actors":["达米安·萨格","希西莉亚·卡拉","葛里高利·巴奎特","Tom Ross"],"is_watched":false},
            {"rating":["9.3","50"],"rank":23,"cover_url":"https://img2.doubanio.com\/view\/photo\/s_ratio_poster\/public\/p2616355133.jpg","is_playable":true,"id":"3541415","types":["剧情","科幻","悬疑","冒险"],"regions":["美国","英国"],"title":"盗梦空间","url":"https:\/\/movie.douban.com\/subject\/3541415\/","release_date":"2010-09-01","actor_count":28,"vote_count":1570120,"score":"9.3","actors":["莱昂纳多·迪卡普里奥","约瑟夫·高登-莱维特","艾伦·佩吉","汤姆·哈迪","渡边谦","迪利普·劳","基里安·墨菲","汤姆·贝伦杰","玛丽昂·歌迪亚","皮特·波斯尔思韦特","迈克尔·凯恩","卢卡斯·哈斯","李太力","克莱尔·吉尔蕾","马格努斯·诺兰","泰勒·吉蕾","乔纳森·吉尔","水源士郎","冈本玉二","厄尔·卡梅伦","瑞恩·海沃德","米兰达·诺兰","拉什·费加","蒂姆·科勒赫","妲露拉·莱莉","迈克尔·加斯顿","吉尔·马德雷尔","玛格丽特·因索利亚"],"is_watched":false},
            ....
        ]
    
        我们所需的目标数据：电影名称、电影评分分别在每一个大字典的title 及 score字段。

    2.再依次检索第二目标数据：某分类电影总数、所有的电影分类名称及其对应的type值
        F12 -- network -- XHR -- 鼠标滚动不断刷新页面 -- 查看左侧AJAX异步加载项 -- preview 
        
        观察AJAX请求项得知该AJAX接口请求的URL如下：
        https://movie.douban.com/j/chart/top_list_count?type=11&interval_id=100%3A90
        其中type参数可由程序得到，即该请求的URL基本格式如下：
        'https://movie.douban.com/j/chart/top_list_count?type={}&interval_id=100%3A90'
        
        得到的一次AJAX请求的response如下：
        {"playable_count":380,"total":716,"unwatched_count":716}
        
        total字段为当前某分类下的电影总数量
        
    3.最后检索第三目标数据：所有的电影分类名称及其对应的type值
    
        请求URL：https://movie.douban.com/chart
        F12 -- elements -- 抓手 -- 抓到分类级联菜单
        
        <div>
      <h2>分类排行榜 · · · · · ·<img style=" position: absolute;" src="https://img3.doubanio.com/f/shire/e49eca1517424a941871a2667a8957fd6c72d632/pics/new_menu.gif"></h2>
      <div class="types">
          <span><a href="/typerank?type_name=剧情&type=11&interval_id=100:90&action=">剧情</a></span>
          <span><a href="/typerank?type_name=喜剧&type=24&interval_id=100:90&action=">喜剧</a></span>
          <span><a href="/typerank?type_name=动作&type=5&interval_id=100:90&action=">动作</a></span>
          <span><a href="/typerank?type_name=爱情&type=13&interval_id=100:90&action=">爱情</a></span>
          <span><a href="/typerank?type_name=科幻&type=17&interval_id=100:90&action=">科幻</a></span>
          <span><a href="/typerank?type_name=动画&type=25&interval_id=100:90&action=">动画</a></span>
          <span><a href="/typerank?type_name=悬疑&type=10&interval_id=100:90&action=">悬疑</a></span>
          ...
          
        所需的类型名称及对应的type值在a标签的href属性中，采用正则表达式提取：
        r'<a href=.*?type_name=(.*?)&type=(.*?)&.*?</a>'
        
实现步骤：
1.确定基准URL
2.向第二目标数据的AJAX接口发送请求获取电影总数
3.向第三目标数据的URL页面发起请求获取电影分类名称及对应type值
4.拼接parmas参数
3.向第一目标数据的AJAX接口发送请求，获取电影名称及其对应评分      

"""


class DouBanMovieCommentsSpider(object):
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
        if not hasattr(DouBanMovieCommentsSpider, '_instance'):
            with DouBanMovieCommentsSpider._instance_lock:
                if not hasattr(DouBanMovieCommentsSpider, '_instance'):
                    DouBanMovieCommentsSpider._instance = object.__new__(cls)
        return DouBanMovieCommentsSpider._instance

    def __init__(self):
        self.__url = 'https://movie.douban.com/j/chart/top_list?'
        self.__headers = {
            'User-Agent':UserAgent().random
        }
        self.__i = 0

    def __get_page(self,parmas):
        return requests.get(url=self.__url,params=parmas,headers=self.__headers).json()

    def __parse_html(self,html):
        dict = {}
        # 调用get_page返回的响应为大列表：[{电影1信息},{},...,{}]
        for item in html:
            dict[item['title'].strip()] = float(item['score'].strip())
            # dict['name'] = item['title'].strip()
            # dict['score'] = float(item['score'].strip())
            self.__i += 1
        print(dict)

    def __get_total(self,type_number):

        #控制台抓包得到的另一XHR请求对象
        url = 'https://movie.douban.com/j/chart/top_list_count?type={}&interval_id=100%3A90'.format(type_number)
        return int(requests.get(url=url,headers=self.__headers).json()['total'])

    #获取所有电影分类名称及其对应type值
    def __get_all_type(self):
        # 获取类型码
        url = 'https://movie.douban.com/chart'
        html = requests.get(url=url, headers=self.__headers).text
        r_list = re.findall(r'<a href=.*?type_name=(.*?)&type=(.*?)&.*?</a>',html)
        # 存放所有类型和对应类型码大字典
        type_dict = {}
        menu = ''
        for r in r_list:
            type_dict[r[0].strip()] = r[1].strip()
            # 获取input的菜单，显示所有电影类型
            menu += r[0].strip() + '|'
        return type_dict, menu


    def display(self):
        type_dict, menu = self.__get_all_type()
        menu = menu + '\n请做出你的选择：'
        name = input(menu)
        type_number = type_dict[name]
        total = self.__get_total(type_number)
        for begin in range(0,(total + 1),20):
            parmas = {
                'type': type_number,
                'interval_id': '100:90',
                'action': '',
                'start': str(begin),
                'limit': '20'
            }
            self.__parse_html(self.__get_page(parmas))
            time.sleep(random.randint(0,3))
        print('电影数量：%d'%self.__i)

def test():
    DouBanMovieCommentsSpider().display()

if __name__ == '__main__':
    test()








