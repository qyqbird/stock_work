#-*- coding:utf-8 -*-
#Date:2017-05-03
#Author:yuqing.qin
#desc: 连续几天缩量的股票容易涨，导出最近连续缩量的股票程序
import tushare as ts
import sys
import numpy as np
sys.path.append('../stock_select')
from download import DownLoad,TS



def judge_shrinkage(data, threshold=0.02):
    recentdata = data[-4:]
    recentdata.index = [1,2,3,4]
    yesterday_close = data[-5:-1]['close']
    yesterday_close.index = [1,2,3,4]
    recentdata['yesterday_close'] = yesterday_close
    recentdata['amplitude'] = (recentdata['close'] - recentdata['yesterday_close']) / recentdata['yesterday_close']
    # 根据振幅判断
    mean = np.mean(recentdata['amplitude'])
    #几个硬指标
    if recentdata.ix[4]['amplitude'] < threshold and recentdata.ix[3]['amplitude'] < threshold and recentdata.ix[2]['amplitude'] < threshold:
        if recentdata.ix[1]['amplitude'] < threshold:
            return 4, mean
        else:
            return 3,mean
    else:
        return -1


class Shrinkage(object):
    def __init__(self):
        pass

    def process(self):
        fo = open('shrink_code', 'w')
        rawdata = TS.memchaced_data(ts.get_stock_basics,'get_stock_basics')
        for code in raw_data.index:
            daydata = ts.get_k_data(code, ktype='D')
            flag, mean = judge_shrinkage(daydata)
            if flag != -1:
                fo.write("{0}\t{1}\t{2}\n".format(flag,code, mean))
        fo.close()


if __name__ == '__main__':
    shri = Shrinkage()
    shri.process()