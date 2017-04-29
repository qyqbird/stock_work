# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20151019
import datetime
import talib as ta
import numpy as np
import matplotlib.pyplot as plotting
from matplotlib.dates import date2num
from matplotlib.finance import candlestick_ochl,candlestick2_ochl
import matplotlib.pyplot as plt
from pandas import DataFrame
from download import DownLoad




class BackTest2(object):
    def __init__(self,data,short_period=8,long_period=22,matype=1):
        self.raw_data = data   #回测历史数据
        self.left_money = 100000.0 #初始资金
        self.init_money = 100000.0 #初始资金
        self.shares = 0     #股票数
        self.state = 0  #状态，控制仓位，已经买入金额
        
        self.money = [] #money的时间图
        self.buy_price = 10000000.0    #买入价位
        self._init_params(short_period,long_period,matype)

    def _init_params(self,short_period,long_period,matype):
        self.raw_data['num'] = self.raw_data.index
        self.raw_data.index = self.raw_data['date']
        H1 = ta.MA(np.asarray(self.raw_data['close']), timeperiod=short_period,matype=1) #快线
        H2 = ta.MA(H1, timeperiod=long_period,matype=matype) #慢线
        self.raw_data['line1'] = H1-H2
        self.raw_data['H1'] = H1
        self.raw_data['H2'] = H2

        ma5 = ta.MA(np.asarray(self.raw_data['close']), timeperiod=5) #快线
        ma10 = ta.MA(np.asarray(self.raw_data['close']), timeperiod=20) #慢线
        self.raw_data['line2'] = ma5 - ma10
        self.raw_data['ma5'] = ma5
        self.raw_data['ma10'] = ma10

    def buy_all(self,open_price,day):
        self.buy_price = open_price
        shares = int(self.left_money / open_price/100)
        self.shares += shares
        self.left_money -= shares * open_price * 100
        self.state = 2  #全仓
        if shares >0:
            print "{0} 同时上穿，以价格:{1} 购买了股票:{2}手,总共持有股票:{3}手,已经满仓了,可用资金:{4}".format(day,
                open_price,shares,self.shares, self.left_money)                

    def buy_half(self,open_price,day):
        self.buy_price = open_price
        shares = int(self.left_money /2/ open_price/100)
        self.shares += shares
        self.left_money -= shares * open_price * 100
        self.state = 1  #半仓
        if shares > 0:
            print "{0} 单根上穿，以价格:{1} 购买了股票:{2}手,总共持有股票:{3}手,可用资金:{4}".format(day,
                open_price,shares,self.shares, self.left_money)                
   
    def sell_half(self,open_price,day):
        shares = int(self.shares/2)
        self.left_money += shares * open_price * 100
        self.shares -= shares
        self.state = 1
        if shares > 0:
            print "{0} 一根线下穿了，以价格:{1} 卖出股票:{2}手,总共持有股票:{3}手,已经半仓了,可用资金:{4}".format(day,
                open_price,shares,self.shares, self.left_money)

    def sell_all(self,open_price,day):
        shares = self.shares
        self.left_money += shares * open_price * 100
        self.shares -= shares
        self.state = 0
        if shares > 0:
            print "{0} 均下穿，以价格:{1} 卖出股票:{2}手,总共持有股票:{3}手,已经清仓了,可用资金:{4}".format(day,
                open_price,shares,self.shares, self.left_money)

    def sell_discount(self,open_price,day,discount):
        '''
        按照discount 卖出仓位，初始仓位怎么获取
        '''
        shares = int(self.shares * discount)
        self.left_money += shares * open_price * 100
        self.shares -= shares
        self.state = 1
        if shares > 0:
            print "{0} 保护利润，以价格:{1} 卖出股票:{2}手,还剩股票:{3}手,可用资金:{4}".format(day,
                open_price,shares,self.shares, self.left_money)
    #H1,H2,ma    
    def check_every_day(self,start,end):
        '''
        回测某一段时间范围
        '''
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
        #
        idx_start = self.raw_data.ix[start]['num']
        idx_end = self.raw_data.ix[end]['num']
        self.raw_data.index = self.raw_data['num']
        for idx in self.raw_data[idx_start:idx_end].index:
            #均线信号
            day = self.raw_data.ix[idx]['date']
            open_price = self.raw_data.ix[idx]['open']
            close_price = self.raw_data.ix[idx]['close']
            ma_signal = self.signal(self.raw_data.ix[idx-2]['line2'],self.raw_data.ix[idx-1]['line2'])
            ema_signal = self.signal(self.raw_data.ix[idx-2]['line1'],self.raw_data.ix[idx-1]['line1']) 

            #空仓时候
            if self.state == 0:
                #同时上穿，买入全仓              
                if ma_signal and ema_signal:
                    self.buy_all(open_price,day)
                #ma 领先ema上穿,买入半仓
                elif ma_signal or ema_signal:
                    self.buy_half(open_price,day)
            #半仓时候
            elif self.state == 1:
                #买入
                if ma_signal and ema_signal:
                    self.buy_all(open_price,day) 
                #卖出
                elif not ma_signal and not ema_signal:
                    self.sell_all(open_price,day)
            elif self.state == 2:
                #全卖出
                if not ma_signal and not ema_signal:
                    self.sell_all(open_price,day)
                elif ma_signal or ema_signal:
                    self.sell_half(open_price,day)
            else:
                print 'ERROR state {0}'.format(self.state)

            value = self.shares * 100 * close_price
            self.money.append(self.left_money + value)

        if self.init_money < self.money[-1]:
            ratio = (self.money[-1]-self.init_money)/self.init_money
            print "--盈利--,总资产:{0} 盈利{1}".format(self.money[-1], ratio)
            return self.money[-1],"赚{0}".format(ratio)
        else:
            ratio = (self.init_money-self.money[-1])/self.init_money
            print "--亏损--,总价值:{0} 亏损{1}".format(self.money[-1],ratio)
            return self.money[-1],"亏{0}".format(ratio)
    
    #H1 H2
    def strategy2(self, start, end):
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
        #
        idx_start = self.raw_data.ix[start]['num']
        idx_end = self.raw_data.ix[end]['num']
        self.raw_data.index = self.raw_data['num']
        for idx in self.raw_data[idx_start:idx_end].index:
            #均线信号
            day = self.raw_data.ix[idx]['date']
            open_price = self.raw_data.ix[idx]['open']
            close_price = self.raw_data.ix[idx]['close']
            ema_signal = self.signal(self.raw_data.ix[idx-2]['line1'],self.raw_data.ix[idx-1]['line1'])     

            if self.state == 0:
                if ema_signal:
                    self.buy_half(open_price,day)
            elif self.state == 1:
                if ema_signal:
                    self.buy_all(open_price,day)
                if not ema_signal:
                    self.sell_all(open_price,day)
            elif self.state == 2:
                if not ema_signal:
                    self.sell_all(open_price,day)
            else:
                print "ERROR state{0}".format(self.state)
            value = self.shares * 100 * close_price
            self.money.append(self.left_money + value)

        if self.init_money < self.money[-1]:
            print "--盈利--,总资产:{0} 盈利{1}".format(self.money[-1],(self.money[-1]-self.init_money)/self.init_money )
        else:
            print "--亏损--,总价值:{0} 亏损{1}".format(self.money[-1],(self.init_money-self.money[-1])/self.init_money)

    
    def strategy3(self, start, end):
        '''
        H1 H2 金叉，全仓买入
        5%卖出2/5
        10%卖出1/5
        剩余死叉卖出
        '''
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
        #
        idx_start = self.raw_data.ix[start]['num']
        idx_end = self.raw_data.ix[end]['num']
        self.raw_data.index = self.raw_data['num']
        for idx in self.raw_data[idx_start:idx_end].index:
            #均线信号
            day = self.raw_data.ix[idx]['date']
            open_price = self.raw_data.ix[idx]['open']
            close_price = self.raw_data.ix[idx]['close']
            ema_signal = self.signal(self.raw_data.ix[idx-1]['line1'],self.raw_data.ix[idx]['line1'])     

            if self.state == 0:
                if ema_signal == 1:
                    self.buy_all(open_price,day)
            elif self.state == 1:
                if ema_signal == 1:
                    #保护利润
                    if (close_price-self.buy_price)/self.buy_price >=0.07:
                        self.sell_discount(close_price,day,1.0/3)                                    
                elif ema_signal == -1:
                    self.sell_all(open_price,day)
            elif self.state == 2:
                if ema_signal == -1:
                    self.sell_all(open_price,day)
                else:
                    if (close_price-self.buy_price)/self.buy_price >=0.05:
                        self.sell_discount(close_price,day,0.6) 
            else:
                print "ERROR state{0}".format(self.state)
            value = self.shares * 100 * close_price
            self.money.append(self.left_money + value)

        if self.init_money < self.money[-1]:
            print "--盈利--,总资产:{0} 盈利{1}".format(self.money[-1],(self.money[-1]-self.init_money)/self.init_money )
        else:
            print "--亏损--,总价值:{0} 亏损{1}".format(self.money[-1],(self.init_money-self.money[-1])/self.init_money)

    def draw_result(self,start,end,sh):
        fig = plt.figure()
        ax = fig.add_subplot(311)
        self.raw_data.index = self.raw_data['date']
        raw_data = self.raw_data[start:end]
        raw_data['time'] = raw_data['date'].map(date2num)

        #K线 信号
        data = DataFrame(raw_data, columns=['time', 'open','close','high','low'])
        data = np.array(data)
        candlestick_ochl(ax,data,width=0.6,colordown=u'g',colorup=u'r')

        plt.grid()
        plt.plot(raw_data['date'], raw_data['H1'], color='r',label='H1')
        plt.plot(raw_data['date'], raw_data['H2'], color='y',label='H2')

        #大盘
        ax = fig.add_subplot(312)
        plt.grid()      
        sh.index = sh['date']
        sh_data = sh[start:end]
        sh_data['time'] = sh_data['date'].map(date2num)
        df = DataFrame(sh_data, columns=['time', 'open','close','high','low'])
        print df['time']
        df = np.array(df)
        candlestick_ochl(ax,df,width=0.6,colordown=u'g',colorup=u'r')

        #收益图
        plt.subplot(3,1,3)
        plt.grid()
        print len(self.money),len(raw_data.index)
        plt.plot(raw_data['date'],self.money)

        # plt.subplot(3,1,3)
        # plt.grid()
        # plt.plot(raw_data['date'], raw_data['line1'], color='b',label='line1')
        plt.show()

    @staticmethod
    def signal(yesterday, today):
        if yesterday < 0.0:
            if today < 0.0:
                return -1
            else:
                return 1
        elif yesterday == 0.0:
            if today <=0.0:
                return -1
            if today >0.0:
                return 1
        else:
            if today <=0:
                return -1
            else:
                return 1

    @staticmethod
    def signal2(before,yesterday, today):
        '''
        发出买入卖出信号
        '''
        if yesterday <= 0 and today <=0:
            return 0 #继续空仓
        if yesterday <0 and today >0:
            return 1 #买入
        if yesterday >0 and today >0:
            return 1 #买入
        #实际上这里卖出已经有点晚了
        if yesterday >0 and today <=0:
            return -1 #卖出
        return 0

def multiple_test():
    dl = DownLoad()
    raw_data = dl.load_data('600059')
    bt1 = BackTest2(raw_data,8,22,1)    #ema
    bt1.strategy2('2014-01-09','2015-02-26')
    bt2 = BackTest2(raw_data,8,22,2)    #wma 
    bt2.strategy2('2014-01-09','2015-02-26')
    bt3 = BackTest2(raw_data,8,22,3)    #3=DEMA,
    bt3.strategy2('2014-01-09','2015-02-26')
    bt4 = BackTest2(raw_data,8,22,4)    #4=TEMA, 
    bt4.strategy2('2014-01-09','2015-02-26')
    bt5 = BackTest2(raw_data,8,22,5)    #5=TRIMA, 
    bt5.strategy2('2014-01-09','2015-02-26')
    bt6 = BackTest2(raw_data,8,22,6)    #6=KAMA,
    bt6.strategy2('2014-01-09','2015-02-26')
    bt7 = BackTest2(raw_data,8,22,7)    #7=MAMA
    bt7.strategy2('2014-01-09','2015-02-26')


def some_tt(start,end,sh):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.grid()      
    sh.index = sh['date']
    sh_data = sh[start:end]
    #.loc[row_indexer,col_indexer] = value instead
    sh_data['time'] = sh_data['date'].map(date2num)
    df = DataFrame(sh_data, columns=['time', 'open','close','high','low'])
    df = np.array(df)
    candlestick_ochl(ax,df,width=0.6,colordown=u'g',colorup=u'r')
    ax.set_title('Some Test') 
    ax.xaxis_date()
    plt.show()


if __name__ == '__main__':
    dl = DownLoad()
    #raw_data = dl.load_data('002429')
    #aw_data = dl.load_data('600059')
    sh = dl.load_data('000001')
    some_tt('2014-01-09','2015-02-25',sh)
    # bt = BackTest2(raw_data)
    # # bt.strategy3('2014-01-09','2014-05-26')
    # # bt.draw_result('2014-01-09','2014-05-25')   #时间截止的区别，这里要少一天对应

    # bt.strategy3('2014-01-09','2015-02-26')
    # bt.draw_result('2014-01-09','2015-02-25',sh)   #时间截止的区别，这里要少一天对应