#-*- coding:utf-8 -*-
#Date:2016-11-27
#Author:yuqing.qin
#desc: 实现唐主任的十步选股法
#引用：http://weibo.com/ttarticle/p/show?id=2309403967380018599156

import tushare as ts
import talib as ta
import numpy as np
from pandas import DataFrame
import pandas.io.sql as SQL
from sqlalchemy import create_engine
import sys
sys.path.append('../utility')
sys.path.append('../stock_select')
from download import DownLoad,TS


def macd_judge(macdyellow,macdblue,macdhist,leftthreshold, rigththreshold):

    def macd_hist(macdhist):
        '''
        判断MCAD 柱子曲线 是否是合适介入的状态
        param: macdhist 今天排在倒数第一个
               threshold  柱子阈值，大于某个值才选择
        '''
        flag = False
        try:
            if macdhist[-1] < leftthreshold or macdhist[-1] > rigththreshold:
                return flag
            mean_today = np.sum(macdhist[-6:-1]) / 5
            mean_before = np.sum(macdhist[-9:-4]) / 5
            #抽象为 最近5天的macd 平均 是大于前3天的平均MACD的
            if mean_today > mean_before and macdhist[-1] > macdhist[-2]:
                flag = True 
        except Exception,e:
            pass
        return flag

    def macd_yell_blue(macdyellow, macdblue, threshold):
        '''
        判断MCAD 黄蓝线相对位置，及大小是否合适介入
        '''
        if macdyellow < threshold and macdblue < threshold:
            return True
        else:
            return False
    return macd_hist(macdhist)
def kdj_judge(slowk, slowd):
    '''
    KDJ比较敏感，需要仔细的调节
    '''
    C = slowk - slowd
    #1. 已经金叉
    mean5 = np.sum(C[-5:]) / 5
    flag = False
    if C[-1] > mean5:
        if C[-1] > 0 and slowk[-2] > slowd[-2]:
            flag = True
        if C[-1] < 0 and C[-1] > -10.0 and C[-1] > C[-2] and C[-2] >= C[-3]:
            falg = True

    return falg

def tang_method(data, leftthreshold, rigththreshold):
    flag = False
    try:
        macdyellow, macdblue, macdhist = ta.MACD(np.asarray(data['close']), fastperiod=12, slowperiod=26, signalperiod=9)
        if macd_judge(macdyellow, macdblue, macdhist, leftthreshold,rigththreshold):
            #slowk, slowd = ta.STOCH(np.asarray(data['high']),np.asarray(data['low']), np.asarray(data['close']), 
            #                            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
            # if kdj_judge(slowk, slowd):
            #     flag = True
            flag = True
    except Exception, e:
        pass
    return flag



class TangPlan(object):
    def __init__(self):
        #用于本地Mysql 获取数据
        self.init_foundmental_data()

    def __del__(self):
        pass

    def init_foundmental_data(self):
        self.foundmental_data = TS.memchaced_data(ts.get_stock_basics,'get_stock_basics')
        self.foundmental_data['earn_ratio'] = self.foundmental_data['esp'] / self.foundmental_data['bvps']
        print "获取基本数据，并且计算净资产收益率"

    def tang_process(self):
        badarea = set(['黑龙江','辽宁','吉林'])
        raw_data = self.foundmental_data
        month_writer = open('month_health', 'w')
        week_writer = open('week_health', 'w')
        day_writer = open('day_health', 'w')
        for code in raw_data.index:
            earn_ratio = raw_data.ix[code]['earn_ratio']
            if raw_data.ix[code]['area'] in badarea:
                continue
            monthdata = ts.get_k_data(code, ktype='M')
            weekdata = ts.get_k_data(code, ktype='W')
            daydata = ts.get_k_data(code, ktype='D')

            if tang_method(monthdata, -0.8, 1.5):
                month_writer.write(code + '\t' + str(earn_ratio) + '\n')
                if tang_method(weekdata, -0.5, 0.8):
                    week_writer.write(code + '\t' + str(earn_ratio) + '\n')
                    if tang_method(daydata,-0.2, 0.6):
                        day_writer.write(code + '\t' + str(earn_ratio) + '\n')
                        print code
            sys.stdout.flush()

        month_writer.close()
        week_writer.close()
        day_writer.close()

    def month_good(self):
        '''
        TODO：访问自己的mysql，节约取数据时间
        '''
        raw_data = self.foundmental_data
        ban_data = self.lift_ban_stock()
        for code in raw_data.index:
            table_name = 'day_{0}'.format(code)
            data = None
            try:
                data = SQL.read_sql('select * from {0}'.format(table_name), self.connection)
            except Exception,e:
                print "Load {0} ERROR".format(table_name)
                print e
                continue

if __name__ == '__main__':
    tang = TangPlan()
    tang.tang_process()
