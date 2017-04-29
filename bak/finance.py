# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20151016
from ctypes import *
import string
import tushare as ts
from sqlalchemy import create_engine
from sqlalchemy import Table
from pandas import *
import datetime

'''
表设计
1. 基本上不变信息：基本数据
2. 日期，分时，价格，有必要下载所有的么  => 周线，月线，等数据
3. stock,日期，均线表 =>5分钟，15分钟等数据
因此暂时就存这三个表了
'''
def str2date(input):
    return datetime.datetime.strptime(input, "%Y-%m-%d")

def date2str(today=None):
    if today == None:
        today =datetime.date.today()
    return today.strftime("%Y-%m-%d")

def deal_list():
    stock = "000001"
    engine = create_engine('mysql://root:123456@127.0.0.1/finance?charset=utf8')
    deals = ts.get_tick_data(stock, date='2015-10-16')
    table_name = stock + '_deal'
    deals.to_sql(table_name, engine)

class DownLoadHistory(object):
    def __init__(self):
        self.engine = create_engine('mysql://root:123456@127.0.0.1/finance?charset=utf8')

    def ktype_history_info(self, stock, engine):
        '''
        下载某个股票历史数据，并且存储到mysql
        '''
        day_stick = ts.get_hist_data(stock)
        #day_stick.to_sql(stock, engine, if_exists='append')
        #day_stick['date'] = day_stick.index
        day_stick.index = day_stick.index.map(str2date)
        day_stick.to_sql(stock, engine)

    def deal_list_download(self, stock, engine, start='2014-10-16'):
        '''
        分时数据下载
        '''
        deals = ts.get_tick_data(stock, date='2015-10-16')
        table_name = stock + '_deal'
        deals.to_sql(table_name, engine) 

    def kstick_list_download(self):
        '''
        下载所有的历史数据
        '''
        stocks = ts.get_stock_basics()
        for stock in stocks.index:
            print 'download stock:', stock
            self.ktype_history_info(stock, self.engine)


def ktype_history_info(stock, engine):
    '''
    下载某个股票历史数据，并且存储到mysql  
    '''
    day_stick = ts.get_h_data(stock,index=True) #前复权
    print day_stick.shape
    print day_stick.index
    day_stick.to_sql(stock, engine)

#分段下载，下载所有历史数据
def down_all_history(stock):
    basic = ts.get_stock_basics()
    date = basic.ix[stock]['timeToMarket']
    start = date2str(date)
    
if __name__ == '__main__':
    #dlh = DownLoadHistory()
    #下载几个股票所有历史数据
    #ktype_history_info('002506', dlh.engine)
    #ktype_history_info('002030', dlh.engine)
    #ktype_history_info('hs300', dlh.engine)
    #ktype_history_info('399106', dlh.engine) #深圳综合指数
    #deal_list()
    data = ts.get_h_data('002337',start='2010-01-01',end='2011-03-16') #两个日期之间的前复权数据
    print data.columns
    print data.shape
    print data.index