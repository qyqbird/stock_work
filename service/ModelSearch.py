#-*- coding:utf-8 -*-
#Date:2017-05-03
#Author:yuqing.qin
#desc: 连续几天缩量的股票容易涨，导出最近连续缩量的股票程序
import tushare as ts
import talib as ta
import sys
import numpy as np
from collections import defaultdict
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

bad_container = set(['300372'])

def recent_k_amplitude(data, threshold):
    '''
    判断股票周线是振幅萎缩情况
    '''
    number = 0
    try:
        recentdata = data[-5:]
        recentdata.index = [5,4,3,2,1]
        recentdata['kwidth'] = (recentdata['close'] - recentdata['open']) / recentdata['open']
        for ratio in recentdata['kwidth']:
            if ratio<= threshold and ratio >=threshold:
                number += 1
    except Exception,e:
        return number
    return number

def period_amplitude(data, period):
    '''
    股票区间涨跌幅
    '''
    ratio = None
    try:
        piece = data['close'][-period:]
        high = np.max(piece)
        close = np.array(piece)[-1]
        ratio = (close - high) / high
    except Exception,e:
        pass
    return ratio

def recent_k_macd(data):
    def recent_macdgoldcross_info(macdhist):
        recent = macdhist[-8:]
        max = np.max(recent)
        min = np.min(recent)
        cross_flag = False
        nearcross_falg = False
        if max > 0 and min < 0 and macdhist[-1]>0:
            cross_flag = True
        if max < 0 and min < 0:
            mean3 = np.mean(macdhist[-3:])
            mean6 = np.mean(macdhist[-6:])
            if mean3 > mean6:
                nearcross_falg = True
        mean = np.mean(macdhist[-4:])
        return cross_flag, nearcross_falg, mean

    macdwhite, macdyellow, macdhist = ta.MACD(np.asarray(data['close']), fastperiod=12, slowperiod=26, signalperiod=9)
    macdhist = macdhist * 2
    return recent_macdgoldcross_info(macdhist)

def period_k_meanline(data, period):
    '''
    重要周线信息
    '''
    

def compute_foundation_info(code, data, period):
    '''
    计算股票一些信息
    '''
    info = {}
    info['code'] = code
    info['ratio'] = period_amplitude(data,period)
    info['week_shrink'] = recent_k_amplitude(data,0.02)
    info['close'] = data['close'].tail(1).values[0]
    cross_flag, nearcross_falg, macdmean = recent_k_macd(data)
    info['cross_flag'] = cross_flag
    info['nearcross_flag'] = nearcross_falg
    info['macdmean'] = macdmean

    return info

features = ['code','week_shrink','ratio', 'cross_flag', 'nearcross_flag', 'macdmean','close']
class Shrinkage(object):
    def __init__(self):
        pass

    def process(self):
        week_shrink = open('week_shrink','w')
        raw_data = ts.get_stock_basics()
        raw_data['earn_ratio'] = raw_data['esp'] / raw_data['bvps']
        container = defaultdict(list)
        for code in raw_data.index:
            if code in bad_container:
                continue
            weekdata = ts.get_k_data(code, ktype='W')
            try:
                info = compute_foundation_info(code, weekdata, 36)
                if info['ratio'] > 0.2:
                    continue
                if not info['cross_flag'] and not info['nearcross_flag']:
                    continue
                if info['macdmean'] > 0.3:
                    continue
                assment = info['close'] * raw_data.ix[code]['totals']
                if info['week_shrink'] < 2 or info['close'] < 6 or assment > 1800:
                    continue
                for feature in features:
                    feature_value = info[feature]
                    container[feature].append(feature_value)
            except Exception,e:
                print "ERROR:{0}".format(code)

        #排序
        clean_data = pd.DataFrame(container,columns=features)
        clean_data = clean_data.sort_values('week_shrink', ascending=False)
        clean_data = clean_data.sort_values('ratio')
        for index in clean_data.index:
            strformat = '\t'.join(clean_data.ix[index].tolist())
            week_shrink.write(strformat + "\n")
        week_shrink.close()


if __name__ == '__main__':
    shri = Shrinkage()
    shri.process()
