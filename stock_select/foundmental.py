#-*- coding:utf-8 -*-
import tushare as ts
from datetime import datetime,timedelta
import time
import cPickle
import math
import copy
import sys
from pandas import DataFrame 
import pandas as pd
sys.path.append('../utility')
from download import DownLoad,TS

def interval_time(middle_str, delta=15):
    middle = datetime.strptime(middle_str,'%Y-%m-%d')
    start = middle - timedelta(delta)
    end = middle + timedelta(delta)
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

class StockSelect(object):
    '''
    思路 1.比价系统，比教同时间内个股与大盘差异化，选出跌幅最大的或者涨幅最小的股票
    '''
    def __init__(self):
        #1. 获取基本数据
        self.init_foundmental_data()
        self.init_profit_data()

    def init_foundmental_data(self):
        self.foundmental_data = TS.memchaced_data(ts.get_stock_basics,'get_stock_basics')
        self.foundmental_data['earn_ratio'] = self.foundmental_data['esp'] / self.foundmental_data['bvps']
        print "获取基本数据，并且计算净资产收益率"
    def init_profit_data(self):
        #1. 初始化财报时间
        season_table = [0,3,4,4,4,1,1,1,2,2,2,3,3]
        now_time = time.localtime()
        season = season_table[now_time.tm_mon]
        year = now_time.tm_year
        if now_time.tm_mon < 5:
            year -= 1
        self.profit_data = TS.memchaced_data(ts.get_profit_data,'get_profit_data',year,season)
        self.profit_data.index = self.profit_data['code']
        print "获取毛利润率财报表时间:{0}年{1}季度".format(year, season)

    def market_index_percent(self,start):
        '''
            1.默认是上海指数,False,为深圳指数  2. 起始时间
            return:这段时间内大盘的变化幅度
            二期，考虑如何返回板块指数
        '''
        sh = TS.memchaced_data(ts.get_h_data,'sh','000001', index=True) #上证指数
        sz = TS.memchaced_data(ts.get_h_data,'sz','399001', index=True) #深圳综合指数
        self.delta_compute(sh,'上海指数','2015-12-01')
        self.delta_compute(sz,'深圳指数','2015-12-01')

    def delta_compute(self, raw_data, name, start):
        end_point = raw_data.head(1)['close'].values[0]
        start, end = interval_time(start)
        data = raw_data[end:start]
        if data.empty:
            print '{0} 历史数据处于停牌区间，注意'.format(name)
            start, end = interval_time(end,25)
            data = raw_data[end:start]
        if data is None:
            return None
        start_point = max(data['close'])
        if start_point < end_point:
            start_point = min(data['close'])

        delta = end_point - start_point
        percent = delta / start_point
        if delta > 0:
            print "name:{0} start:{1} end:{2} 时间区间:{3} {4} 涨幅:{5:.1%}".format(name,start_point, end_point,start, end,percent)
        else:
            print "name:{0} start:{1} end:{2} 时间区间:{3} {4} 跌幅:{5:.1%}".format(name,start_point, end_point,start, end,percent)
        return percent

    def list_stock_percent(self, stock_list, start):
        for stock, name in stock_list.iteritems():
            stock_data = TS.memchaced_data(ts.get_h_data,stock,stock) #股票数据
            if stock_data is not None:
                self.delta_compute(stock_data, name, start)

    def list_stock_info(self, stock_list):
        keys = stock_list.keys()
        data = DataFrame(self.foundmental_data, index=keys)
        data = data.sort(columns='earn_ratio', ascending=False)   
        for code in data.index:
            gross_profit_rate = None   #默认值
            if code in self.profit_data.index:
                gross_profit_rate = self.profit_data.ix[code]['gross_profit_rate']
            #2. 过滤毛利率过低的股票
            if gross_profit_rate and gross_profit_rate < 15:
                continue
            self.print_stock_info(code, data.ix[code],gross_profit_rate)

    #资产净收益率,选择大蓝筹股
    def capital_earn_ratio(self):
        # 1. 每股收益 >0
        result = self.foundmental_data
        result = result[result['esp'] > 0.4]
        #按照净资产收益率排名
        result = result.sort(columns='earn_ratio',ascending=False)
        for code in result.index[:200]:
            gross_profit_rate = None   #默认值
            if code in self.profit_data.index:
                gross_profit_rate = self.profit_data.ix[code]['gross_profit_rate']
            #2. 过滤毛利率过低的股票
            if gross_profit_rate and gross_profit_rate < 15:
                continue
            self.print_stock_info(code, result.ix[code],gross_profit_rate)
    # 概念股票分析
    def concept_analysis(self,concept_code):
        #1. 获取概念相关的股票
        concept = TS.memchaced_data(ts.get_concept_classified,'get_concept_classified')
        concept.index = concept['code']
        concept = concept[concept['c_name'] == concept_code]
        #2
        raw_data = copy.deepcopy(self.foundmental_data)
        raw_data = DataFrame(raw_data,index=concept.index)

        #排序
        #raw_data = raw_data.sort(columns='reservedPerShare',ascending=False)
        print '当前排序1. 资本公积金大 2. 股本小 ，策略待思考 3. 去掉了创业板'
        #raw_data = raw_data.sort(columns='totals')
        raw_data = raw_data.sort_values(by=['totals'])
        raw_data = raw_data.sort_values(by=['reservedPerShare'],ascending=False)
        for code in raw_data.index:
            #if code.startswith('3'):
            #    continue
            gross_profit_rate = None
            if code in self.profit_data.index:
                gross_profit_rate = self.profit_data.ix[code]['gross_profit_rate']
            self.print_stock_info(code,raw_data.ix[code],gross_profit_rate)
    #打印股票详细信息
    @staticmethod
    def print_stock_info(code,row_info, gross_profit_rate=None, ban_info=None):
        '''
        code 是股票代码
        gross_profit_rate 是毛利率
        虽然炒概念，也要炒概念中股票比较优质的资产
        '''
        print "stock:{0} name:{1} 公积金:{2} 股本:{3:.2f}亿 PE:{4} ROE:{5:.3f} 毛利率:{6} 行业:{7} 解禁:{8}".format(code,
                row_info['name'],row_info['reservedPerShare'],row_info['totals']/10000, 
                row_info['pe'],row_info['earn_ratio'],gross_profit_rate,row_info['industry'], ban_info)   

    @staticmethod
    def print_stock_info2(code,row_info, gross_profit_rate=None, ban_info=None,transfer=None):
        '''
        code 是股票代码
        gross_profit_rate 是毛利率
        虽然炒概念，也要炒概念中股票比较优质的资产
        '''
        print "{0}:{1} 公积金:{2} 股本:{3:.2f}亿 PE:{4} ROE:{5:.3f} 毛利率:{6} 解禁:{7} {8} 分红{9} 转股{10}".format(code,
                row_info['name'],row_info['reservedPerShare'],row_info['totals']/10000, 
                row_info['pe'],row_info['earn_ratio'],gross_profit_rate, ban_info, transfer['report_date'],
                transfer['divi'], transfer['shares']) 
    #资本公积金，股本选股，用于高转送行情
    def capital_reserve(self,rePerShare=1, total_share=100000, eps=0.1):
        '''
        '''
        result = self.foundmental_data
        ban_data = self.lift_ban_stock()
        history = self.get_history_high_transfer()
        # 1. 保留公积金 
        result = result[result['reservedPerShare'] > rePerShare]
        # 2. 总股本 
        result = result[result['totals'] <=total_share]
        # 3. 每股收益 >0
        result = result[result['esp'] > eps]
        #按照公积金排序
        result = result.sort(columns='reservedPerShare',ascending=False)
        for code in result.index[:200]:
            gross_profit_rate = None
            ban_info = None
            transfer = None
            if code in self.profit_data.index:
                gross_profit_rate = self.profit_data.ix[code]['gross_profit_rate']
            if code in ban_data.index:
                ban_info = ban_data.ix[code]['ratio']
            if code in history.index:
                pass
                # transfer = history.ix[code]
                # self.print_stock_info2(code, result.ix[code],gross_profit_rate,ban_info,transfer)
            else:
                self.print_stock_info(code, result.ix[code],gross_profit_rate,ban_info)

    def lift_ban_stock(self, interval=6):
        '''
            取即将解禁的股票，默认取半年的
        '''
        raw_data = None
        start_month = int(datetime.strftime(datetime.now(), '%m'))
        start_year = int(datetime.strftime(datetime.now(), '%Y'))
        for month in xrange(start_month, start_month+interval):
            foot = month / 13
            month = month%12
            if month == 0:
                month = 12
            print 'get {0} {1} 解禁数据'.format(start_year+foot, month)
            data = ts.xsg_data(year=(start_year+foot),month=month)
            raw_data = pd.concat([raw_data, data], axis=0)
        raw_data.index = raw_data['code']
        return raw_data

    def get_history_high_transfer(self):
        df = ts.profit_data(top=1500)
        df.index = df['code']
        return df
if __name__ == '__main__':
    # raw_data = ts.get_hist_data('sz',start='2015-01-05',end='2015-01-09')
    # print raw_data
    select = StockSelect()
    #select.concept_analysis(u'养殖业')
    #select.concept_analysis(u'黄金概念')
    #select.capital_reserve()
    select.capital_earn_ratio()
    #select.market_index_percent('2015-12-01')
    #data = TS.load_self_select_stock('self_select_stock.txt')
    #data = TS.load_self_select_stock('lanchou.txt')
    #select.list_stock_percent(data, '2015-12-01')
    #select.list_stock_info(data)
