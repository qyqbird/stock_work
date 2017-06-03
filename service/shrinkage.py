#-*- coding:utf-8 -*-
#Date:2017-05-03
#Author:yuqing.qin
#desc: 连续几天缩量的股票容易涨，导出最近连续缩量的股票程序
import tushare as ts
import sys
import numpy as np
sys.path.append('../utility')
sys.path.append('../stock_select')
from download import DownLoad,TS
import warnings
warnings.filterwarnings("ignore")

bad_container = set(['300372'])

def judge_shrinkage(data, threshold=0.02):
    '''
    判断一致股票日线最近是不是持续缩振幅
    '''
    try:
        recentdata = data[-4:]
        recentdata.index = [1,2,3,4]
        yesterday_close = data[-5:-1]['close']
        yesterday_close.index = [1,2,3,4]
        recentdata['yesterday_close'] = yesterday_close
        recentdata['amplitude'] = (recentdata['close'] - recentdata['open']) / recentdata['open']
        sumamp = np.abs(np.sum(recentdata['amplitude']))

        recentdata['amplitude'] = np.abs(recentdata['amplitude'])
        mean = np.abs(np.mean(recentdata['amplitude']))
        if sumamp > 0.02 or mean > threshold:
            return -1, 0
        #几个硬指标
        if recentdata.ix[4]['amplitude'] < 0.015 and recentdata.ix[3]['amplitude'] < threshold and recentdata.ix[2]['amplitude'] < threshold:
            if recentdata.ix[1]['amplitude'] < threshold:
                return 4, mean
            else:
                if recentdata.ix[1]['amplitude'] < 2*threshold:
                    return 3,mean
        return -1, mean
    except Exception,e:
        return -1, 0


def judge_week_shrinkage(data, threshold=0.02):
    '''
    判断一致股票周线是不是持续缩振幅
    '''
    try:
        recentdata = data[-3:]
        recentdata.index = [1,2,3]
        yesterday_close = data[-4:-1]['close']
        yesterday_close.index = [1,2,3]
        recentdata['yesterday_close'] = yesterday_close
        recentdata['amplitude'] = (recentdata['close'] - recentdata['open']) / recentdata['open']

        #几个硬指标
        if np.abs(recentdata.ix[3]['amplitude']) < threshold and np.abs(recentdata.ix[2]['amplitude']) < threshold and np.abs(recentdata.ix[1]['amplitude']) < threshold:
            return True
        return False
    except Exception,e:
        return False

def judge_oversold(data):
    '''
    判断该股票最近跌幅是多少，是否抄底
    '''
    try:
        jieduan = data['close'][-36:]
        high = np.max(jieduan)
        close = np.array(jieduan)[-1]
        ratio = (close - high) / high
        return ratio
    except Exception,e:
        return 0


class Shrinkage(object):
    def __init__(self):
        pass

    def process(self):
        fo = open('shrink_code', 'w')
        oversold = open('oversold', 'w')
        week_shrink = open('week_shrink','w')
        raw_data = TS.memchaced_data(ts.get_stock_basics,'get_stock_basics')
        raw_data['earn_ratio'] = raw_data['esp'] / raw_data['bvps']
        for code in raw_data.index:
            if code in bad_container:
                continue
            try:
                daydata = ts.get_k_data(code, ktype='D')
                ratio = judge_oversold(daydata)
                if ratio < -0.45:
                    oversold.write("{0}\t{1}\n".format(code, ratio))
                if ratio < 0.2:
                    weekdata = ts.get_k_data(code, ktype='W')
                    if judge_week_shrinkage(code, 0.02):
                        week_shrink.write(code + '\n')
                if ratio > -0.3:
                    continue
                if raw_data.ix[code]['earn_ratio'] < 0.05:
                    continue
                totals = raw_data.ix[code]['totals']
                close = np.array(daydata['close'])[-1]
                if close < 6.5:
                    continue
                if close * totals > 320:
                    continue
                flag,mean = judge_shrinkage(daydata,0.012)
                if ratio > -0.3:
                    continue
                if flag != -1:
                    fo.write("{0}\t{1}\t{2:.1%}\n".format(flag,code, mean))
            except Exception, e:
                    print e
        fo.close()
        oversold.close()
        week_shrink.close()


if __name__ == '__main__':
    shri = Shrinkage()
    shri.process()
