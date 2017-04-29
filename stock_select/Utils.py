#-*- coding:utf-8 -*-
#Date:2017-03-03
#Author:yuqing.qin
#desc:一些工具函数

import numpy as np
import tushare as ts


def amplitude_compute(code):
    '''
    计算一些指数的日均振幅信息
    '''
    rawdata = ts.get_k_data(code,start='2011-10-01', end='2014-05-31')
    rawdata['delta'] = rawdata['high'] - rawdata['low']
    length = len(rawdata.index) - 1
    base = rawdata[rawdata.index < length]['close']
    delta = rawdata[rawdata.index > 0]['delta']
    ave_percent = np.mean(delta / base)
    return ave_percent


def main_index_amplitude():
    '''
    打印主要指数的平均振幅
    '''
    codes = {}
    codes['sh'] = '上证指数'
    codes['sz'] = '深圳成指'
    codes['hs300'] = '沪深300指数'
    codes['sz50'] = '上证50'
    codes['zxb'] = '中小板'
    codes['cyb'] = '创业板'
    for code, value in codes.iteritems():
        ave = amplitude_compute(code)
        str_format = "{0}\t{1:%}".format(value, ave)
        print str_format

main_index_amplitude()

