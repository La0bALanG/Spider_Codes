# -*- coding:utf-8 _*-
"""
@version:
author:weichao_an
@time: 2020/10/13
@file: demo20_shortVideoDownloadsSpider.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:各大短视频平台视频下载（下载视频可能带水印）
"""


import requests
import json
import time
import sys
import re
from ProxyPool.proxyPool import getProxy


class ShortVideoDownloadsSpider(object):

    def __init__(self):

        # self.proxy = {
        #     'http':'http://{}'.format(getProxy().get('proxy'))
        # }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }

    def get_html(self,url):

        return requests.get(url=url,headers=self.headers)

    def ppxDownloads(self,url):

        #1.获取item_id

        try:
            item_id = str(self.get_html(url).url).split('/')[-1].split('?')[0]

        except Exception:
            print('item_id获取出错')
            sys.exit()

        #2.拼接视频接口URL链接：

        v_xhr_url = 'https://h5.pipix.com/bds/webapi/item/detail/?item_id={}&source=share'.format(item_id)

        #3.请求该接口获取响应内容，提取视频名称及下载链接：

        try:
            req_xhr = self.get_html(v_xhr_url)
        except Exception:
            print('接口数据获取失败!响应状态吗：',req_xhr.status_code)
            sys.exit()

        xhr_data = req_xhr.json()
        video_url = xhr_data['data']['item']['video']['video_download']['url_list'][0]['url']
        video_name = xhr_data['data']['item']['content']

        #4.请求视频内容，保存为二进制格式，等待文件写入
        finall_video = self.get_html(video_url).content

        #5.文件写入
        filename = video_name + '.mp4'
        with open(filename,'wb') as f:
            f.write(finall_video)

        return video_name

    def douyinDownloads(self,url):

        # 1.获取item_id

        try:
            item_id = str(self.get_html(url).url).split('/')[5]

        except Exception:
            print('item_id获取出错')
            sys.exit()

        #2.拼接视频接口URL链接：
        v_xhr_url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}'.format(item_id)

        #3.请求该接口获取响应内容，提取视频名称及下载链接：

        try:
            req_xhr = self.get_html(v_xhr_url)
        except Exception:
            print('接口数据获取失败!响应状态吗：',req_xhr.status_code)
            sys.exit()

        xhr_data = req_xhr.json()
        video_url = xhr_data['item_list'][0]['video']['play_addr']['url_list'][0]
        video_name = xhr_data['item_list'][0]['desc']

        #4.请求视频内容，保存为二进制格式，等待文件写入
        finall_video = self.get_html(video_url).content

        #5.文件写入
        filename = video_name + '.mp4'
        with open(filename,'wb') as f:
            f.write(finall_video)

        return video_name


def test():
    '''
    测试用例
    '''

    # print('正在准备代理...')
    project = ShortVideoDownloadsSpider()
    # print('代理准备完毕，本次代理IP为：%s'%project.proxy['http'])
    #
    apps_name = input('请选择一个视频平台>>>：')

    if apps_name == '皮皮虾':

        share_url = input('请输入分享链接(程序会自动识别链接)：')

        print('识别中...')
        time.sleep(1)
        print('识别成功，正在获取下载链接...')
        time.sleep(1)
        print('下载链接获取成功...')
        v_name = project.ppxDownloads(share_url)
        print('开始下载：%s.mp4,视频文件较大，请耐心等待...'%v_name)
        print('下载成功！请至本地目录查看！')

    elif apps_name == '抖音':

        share_str = input('请输入分享链接(程序会自动识别链接)：')
        share_url = re.findall('(https?://[^\s]+)', share_str)[0]

        print('识别中...')
        time.sleep(1)
        print('识别成功，正在获取下载链接...')
        time.sleep(1)
        print('下载链接获取成功...')
        v_name = project.douyinDownloads(share_url)
        print('开始下载：%s.mp4,视频文件较大，请耐心等待...'%v_name)
        print('下载成功！请至本地目录查看！')



if __name__ == '__main__':
    test()




