# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20160404

'''
每天更新K线数据
'''


def compute(start, end):
    delta = start - end
    percent = delta / start
    print percent


compute(32.99,19.78)