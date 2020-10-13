# -*- coding:utf-8 _*-
"""
@version:
author:weichao_an
@time: 2020/10/12
@file: demo10_ProxyPoolProject.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:构建个人IP代理池，工程化应用
"""

import requests
import json

def getAPIInfo():
    '''
    get proxy pool API information
    return:str
    '''

    return requests.get('http://127.0.0.1:5010/').text

def getProxy():
    '''
    get one proxy from proxyPool
    return:dict
    '''

    return json.loads(requests.get('http://127.0.0.1:5010/get').text)

def getProxyCounts():
    '''
    get all proxys,means get how many proxys in proxyPool
    return:str
    '''

    return requests.get('http://127.0.0.1:5010/get_status').text

def getAllProxy():
    '''
    get all proxys
    return:list data,every elements is dict
    '''

    return json.loads(requests.get('http://127.0.0.1:5010/get_all').text)

def delete_proxy(proxy):
    '''
    from proxyPool delete one of a proxy
    return:<class 'requests.models.Response'>
    '''

    return requests.get('http://127.0.0.1:5010/delete/?proxy={}'.format(proxy))

