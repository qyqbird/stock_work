# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20160603
from download import DownLoad
from pandas import DataFrame

'''
做一个回测的框架
1. 传入股票
2. 回调一个函数，也就是策略函数
'''

class Strategy(object):
    '''
    策略函数
    '''
    def __init__(self):
        pass

    @abstractmethod
    def action(self):
        pass

class MeanLine(Strategy):


class BackTest(object):
    def __init__(self, stock, start_time, strategy):
        dl = DownLoad()
        dl.load_data(stock)
