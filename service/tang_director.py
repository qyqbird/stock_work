#-*- coding:utf-8 -*-
#Date:2016-11-27
#Author:yuqing.qin
#desc: 实现唐主任的十步选股法
#引用：http://weibo.com/ttarticle/p/show?id=2309403967380018599156
#引用资料:
import tushare as ts
import talib as ta
from pandas import DataFrame
import pandas.io.sql as SQL
from sqlalchemy import create_engine
sys.path.append('../utility')
from download import DownLoad,TS


def macd_judge(macdyellow,macdblue,macdhist):
    return macd_hist(macdhist)

    def macd_hist(macdhist):
        '''
        判断MCAD 柱子曲线 是否是合适介入的状态
        param: macdhist 今天-1
        '''
        flag = False
        mean5 = np.sum(macdhist[-5:]) / 5
        # if macdhist[-1] >= -0.15 and macdhist[-1] <= 0.2:
        #     #macd 柱子是红色的，且 < 0.25 ,
        #     if macdhist[0] > macdhist[1] and macdhist[0] > mean7 and and macdhist[6] < mean7:
        #         flag = True
        #率柱头缩短，或者红柱头见长
        if macdhist[-1] > macdhist[-2] and macdhist[-2] > macdhist[-3] and macdhist[-3] > macdhist[-4]:
            falg = True
        return flag

    def macd_yell_blue(macdyellow, macdblue):
        '''
        判断MCAD 黄蓝线相对位置，及大小是否合适介入
        '''
        return True

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

def tang_method(data):
    flag = False
    macdyellow, macdblue, macdhist = ta.MACD(np.asarray(data['close']), fastperiod=12, slowperiod=26, signalperiod=9)
    if macd_judge(macdyellow, macdblue, macdhist):
        slowk, slowd = ta.STOCH(np.asarray(data['high']),np.asarray(data['low']), np.asarray(data['close']), 
                                    fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        if kdj_judge(slowk, slowd):
            flag = True
    return flag



class TangPlan(object):
    def __init__():
        #用于本地Mysql 获取数据
        self.engine = create_engine('mysql://root:123456@127.0.0.1/stock_info?chharset=utf8')
        self.connection = self.engine.connect()
        self.init_foundmental_data()
        self.season_writer = None
        self.month_writer = None
        self.week_writer = None
        self.day_writer = None

    def __del__():
        self.season_writer.close()
        self.month_writer.close()
        self.week_writer.close()
        self.day_writer.close()


    def init_foundmental_data(self):
        self.foundmental_data = TS.memchaced_data(ts.get_stock_basics,'get_stock_basics')
        self.foundmental_data['earn_ratio'] = self.foundmental_data['esp'] / self.foundmental_data['bvps']
        print "获取基本数据，并且计算净资产收益率"


    def tang_process(self):
        raw_data = self.foundmental_data
        for code in raw_data.index:
            data = ts.get_hist_data('600848', ktype='M')
            

    def season_good(self,):
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