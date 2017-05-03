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


def judge_shrinkage(data, threshold=0.02):
    try:
        recentdata = data[-4:]
        recentdata.index = [1,2,3,4]
        yesterday_close = data[-5:-1]['close']
        yesterday_close.index = [1,2,3,4]
        recentdata['yesterday_close'] = yesterday_close
        recentdata['amplitude'] = (recentdata['close'] - recentdata['yesterday_close']) / recentdata['yesterday_close']
        sumamp = np.abs(np.sum(recentdata['amplitude']))

        recentdata['amplitude'] = np.abs(recentdata['amplitude'])
        mean = np.abs(np.mean(recentdata['amplitude']))
        if sumamp > 0.02 or mean > threshold:
            return -1, 0
        #几个硬指标
        if recentdata.ix[4]['amplitude'] < 0.01 and recentdata.ix[3]['amplitude'] < threshold and recentdata.ix[2]['amplitude'] < threshold:
            if recentdata.ix[1]['amplitude'] < threshold:
                return 4, mean
            else:
                if recentdata.ix[1]['amplitude'] < 2*threshold:
                    return 3,mean
        return -1, mean
    except Exception,e:
        return -1, 0

class Shrinkage(object):
    def __init__(self):
        pass

    def process(self):
        fo = open('shrink_code', 'w')
        raw_data = TS.memchaced_data(ts.get_stock_basics,'get_stock_basics')
        for code in raw_data.index:
            try:
                totals = raw_data.ix[code]['totals']
                daydata = ts.get_k_data(code, ktype='D')
                if np.array(daydata['close'])[-1] * totals > 320:
                    continue
                flag,mean = judge_shrinkage(daydata,0.012)
                if flag != -1:
                    fo.write("{0}\t{1}\t{2:.1%}\n".format(flag,code, mean))
            except Exception, e:
                    pass
        fo.close()


if __name__ == '__main__':
    shri = Shrinkage()
    shri.process()