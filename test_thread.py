# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/21
@file: test_thread.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:
"""

from threading import Thread

class SpiderThread(Thread):
    def __init__(self,fun):
        super().__init__()
        self.target = fun


    def run(self):
        self.target()


def test():
    pass


l = []

for i in range(4):
    t = SpiderThread(target=test)
    l.append(t)
    t.start()