# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20151023
import tushare as ts
from sqlalchemy import create_engine
import datetime
import time
import pandas as pd
import os
import cPickle
from pandas import DataFrame
import pandas.io.sql as SQL
import sys
from tool_decorator import local_memcached
from tool_class import NoInstance, Singleton

def date2str(date):
    return date.strftime("%Y-%m-%d")

class DownLoad(object):
    '''
    1.下载历史数据
    2. 更新每天数据
    3. 装载历史数据
    4. 单例模式
    '''
    __metaclass__ = Singleton
    def __init__(self,*args, **kwargs):
        self.basic = ts.get_stock_basics()
        self.engine = create_engine('mysql://root:123456@127.0.0.1/stock_info?charset=utf8')
        self.connection = self.engine.connect()

    @staticmethod
    def date2str(today=None):
        if today == None:
            today =datetime.date.today()
        return today.strftime("%Y-%m-%d")

    def down_history(self, stock, index=False):
        '''
        下载历史至今天的数据,可以用于下载新股票
        date,open,high,close,low,volume,amount
        '''
        print '--'*10,"downing ",stock,'--'*10
        date = self.basic.ix[stock]['timeToMarket']
        #20100115  竟然是个整数
        start_year = date/10000
        today =datetime.date.today()
        end_year = int(today.strftime("%Y"))
        suffix = "-" + str(date)[4:6] + "-" + str(date)[6:8]

        raw_data = None

        #针对次新股，今年的股票
        if start_year == end_year:
            raw_data = ts.get_h_data(stock,index)
        for year in range(start_year, end_year):
            start = str(year) + suffix
            right = datetime.datetime.strptime(str(year+1) + suffix, "%Y-%m-%d")-datetime.timedelta(days=1)
            #跨年的应该没有那天上市的公司，所以不存在bug
            end = right.strftime("%Y-%m-%d")
            print start, "-----",end
            data = ts.get_h_data(stock,start=start,end=end,index=index)
            if data is None:
                print None
            else:
                print data.shape
            raw_data = pd.concat([raw_data, data], axis=0)

            #看看是否需要补充最后一段时间的数据
            if (year+1) == end_year and end < today.strftime("%Y-%m-%d"):
                this_year_start = str(year+1) + suffix
                print this_year_start, "-------",today.strftime("%Y-%m-%d")
                data = ts.get_h_data(stock, start=this_year_start, end=today.strftime("%Y-%m-%d"),index=index)
                if data is None:
                    print None
                else:
                    print data.shape
                raw_data = pd.concat([raw_data, data], axis=0)

        raw_data = raw_data.sort_index(ascending=True)
        raw_data.to_sql('day_'+stock, self.engine)
        return raw_data

    def down_all_day_stick(self):
        '''
        下载所有股票的历史数据
        '''
        for stock in self.basic.index:
            try:
                print stock
                self.down_history(stock)
            except Exception ,ex:
                print Exception, ";",ex

    def append_days(self,stock, start, end):
        '''
        添加stock,指定时间范围内的数据
        '''
        data = ts.get_h_data(stock,start=start,end=end)
        data = data.sort_index(ascending=True)  
        data.to_sql('day_'+stock, self.engine,if_exists='append')

    def append_all_days(self, start=None, end=None):
        '''
        添加所有股票数据
        '''
        if start == None:
            start = datetime.datetime.today()
            end = start
        for stock in self.basic['code']:
            self.append_days(stock, start, end)

    def load_data(self, stock):
        '''
        加载股票历史数据
        '''
        search_sql = "select * from {0}".format('day_'+stock)
        raw_data = SQL.read_sql(search_sql, self.engine)
        return raw_data

    def check_is_new_stock(self, stock):
        '''
        检测该股票是否为新上市股票
        结果不需要该函数
        '''
        check_sql = "show tables like '{0}'".format('day_'+stock)
        result = self.connection.execute(check_sql)
        if result.first() == None:
            return True
        else:
            return False

    #默认为近3年数据
    def down_period(self, stock,start=None,end=None):
        raw_data = ts.get_hist_data(stock,start,end)
        return raw_data

#新股如603861 有问题


#封装一下ts接口，同一天不要重复获取数据
#不能实例化
class TS(object):
    __metaclass__ = NoInstance

    @staticmethod
    @local_memcached
    def memchaced_data(funcname, fileprefix):
        '''
        使用方法
        1. funcname  ts的方法名
        2. fileprefix  该方法缓存的文件名字
        3. 后面可以给funcname传参数
        demo:
        data = TS.memchaced_data(ts.get_profit_data, 'get_profit_data',2016,1)
        data = TS.memchaced_data(ts.get_stock_basics,'get_stock_basics')
        '''
        pass
        #raw_data = funcname()
        #return raw_data

    @staticmethod
    def load_self_select_stock(filename):
        code_name = {}
        for line in open(filename):
            line = line.strip()[2:].split('    ')
            #rint line[0], line[1]
            code_name[line[0]] = line[1]
        return code_name



if __name__ == '__main__':
    # dl = DownLoad()
    # dl.down_all_day_stick()
    # raw_data = dl.load_data('000001')
    # print raw_data

    aa = TS.memchaced_data(ts.get_profit_data, 'get_profit_data',2016,1)
    print aa