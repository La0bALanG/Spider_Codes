# -*- coding:utf-8 _*-
"""
@version:
author:weichao_an
@time: 2020/10/10
@file: test_proxy.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:测试proxy_pool相关API接口功能
"""

import requests
from ProxyPool.proxyPool import getProxy,getAPIInfo,getProxyCounts,getAllProxy

get_p = getProxy()['proxy']
print(get_p)