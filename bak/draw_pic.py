# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20151019
import datetime
import tushare as ts
import talib as ta
import numpy as np
from matplotlib.dates import DayLocator,MonthLocator,DateFormatter,WeekdayLocator,date2num
from matplotlib.ticker import MultipleLocator,FormatStrFormatter  
from matplotlib.finance import candlestick_ochl,candlestick2_ochl
import matplotlib.pyplot as plt
from pandas import DataFrame
from download import DownLoad

def str2date(input):
    tmp = datetime.datetime.strptime(input, "%Y-%m-%d")
    return date2num(tmp)

def str2date2(input):
    return datetime.datetime.strptime(input, "%Y-%m-%d")
#将index 转化为日期
def mean_plot():
    '''
    看一下均线数据前几个是什么
    '''
    raw_data = ts.get_hist_data('hs300', start='2015-08-15')
    print raw_data['close'][:8]
    raw_data.index = raw_data.index.map(str2date2)
    raw_data['time'] = raw_data.index 
    ema5 = ta.MA(np.asarray(raw_data['close']), timeperiod=5,matype=1)
    sma5 = ta.MA(np.asarray(raw_data['close']), timeperiod=5)
    '''
    结论这个就是均线
    nan        nan        nan        nan  3828.082   3667.6144
    第五天值为前5天均值[1,2,3,4,5]
    第六天均值[2,3,4,5,6]
    '''
    plt.grid()
    plt.plot(raw_data.index, ema5,color='r')
    plt.plot(raw_data.index, sma5, color='g')
    plt.show()

def Kline_plot(raw_data):
    #raw_data = ts.get_hist_data('hs300', start='2015-07-01')
    #raw_data.index = raw_data.index.map(str2date)
    raw_data['time'] = raw_data.index
    data = DataFrame(raw_data, columns=['time', 'open','close','high','low'])
    alldays = DayLocator()
    months = MonthLocator()
    weekdays = WeekdayLocator()
    month_formater = DateFormatter("%b %Y")
    week_formater = DateFormatter("%m %d")

    ymajorLocator   = MultipleLocator(100) #将y轴主刻度标签设置为0.5的倍数 
    ymajorFormatter = FormatStrFormatter('%1.1f') #设置y轴标签文本的格式 
    yminorLocator   = MultipleLocator(10) #将此y轴次刻度标签设置为0.1的倍数 

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_locator(weekdays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(week_formater)

    ax.yaxis.set_major_locator(ymajorLocator)  
    ax.yaxis.set_major_formatter(ymajorFormatter)
    data = np.array(data)
    candlestick_ochl(ax,data,width=0.6,colordown=u'g',colorup=u'r')
    ax.xaxis_date()
    ax.autoscale_view()
    fig.autofmt_xdate()
    plt.show()

#MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
#SMA simple moving average
#EMA  指数平滑
# SMA = talib.MA(close,30,matype=0)[-1]
# EMA = talib.MA(close,30,matype=1)[-1]
# macd, macdsignal, macdhist = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

def tianbijun_formulation():
    raw_data = ts.get_hist_data('hs300', start='2014-07-01')
    H1 = ta.MA(np.asarray(raw_data['close']), timeperiod=8,matype=1)    #8日指数平滑均线
    H2 = ta.MA(H1, timeperiod=20,matype=1)
    LH = ta.MA(np.asarray(raw_data['close']), timeperiod=240, matype=1) #240指数平滑均线
    high_price = ta.MAX(np.asarray(raw_data['high']), timeperiod=36)
    VAR1 = (high_price - np.asarray(raw_data['close'])) / (high_price - ta.MIN(np.asarray(raw_data['high']), timeperiod=36)) * 100
    VAR2 = ta.MA(VAR1, timeperiod=5)
    VAR3 = ta.MA(VAR2,timeperiod=8)
    if line_cross(VAR2,VAR3) and VAR3 < 20:
        VAR4 = True
    else:
        VAR4 = False
    if np.asarray(raw_data['close']) > 1.3 * ta.MIN(np.asarray(raw_data['high']), 
        timeperiod=60) and VAR4: 
        VAR5 = True 
    else:
        VAR5 = False
    if np.asarray(raw_data['close']) >1000:
        VAR6 = VAR4
    else:
        VAR6 = VAR5

    return VAR6


def line_cross(A, B):
    '''
    计算两组数据，A从下上穿B时，返回1，否则返回0，
    '''
    C = A - B   #介值定理,如果A 从下上穿B，则C[0] <0 C[n] >0
    if C[0]<0 and C[C.shape[0] - 1] >0:
        return 1
    return 0


def draw_tianbijun(stock):
    '''
    先画田碧君的趋势图片
    K线以及公式图片一起画
    '''
    dl = DownLoad()
    raw_data = dl.load_data(stock)
    #raw_data.index = raw_data.index.map(str2date2)
    H1 = ta.MA(np.asarray(raw_data['close']), timeperiod=8,matype=1)    #8日指数平滑均线
    H2 = ta.MA(H1, timeperiod=20,matype=1)

    H3 = ta.MA(np.asarray(raw_data['close']), timeperiod=8,matype=3)    #8日 DEMA
    H4 = ta.MA(H3, timeperiod=20,matype=1)

    H5 = ta.MA(np.asarray(raw_data['close']), timeperiod=8,matype=4)    #8日 DEMA
    H6 = ta.MA(H5, timeperiod=20,matype=1)

    #LH = ta.MA(np.asarray(raw_data['close']), timeperiod=240, matype=1) #240指数平滑均线
    #high_price = ta.MAX(np.asarray(raw_data['high']), timeperiod=36)
    #VAR1 = (high_price - np.asarray(raw_data['close'])) / (high_price - ta.MIN(np.asarray(raw_data['high']), timeperiod=36)) * 100
    #VAR2 = ta.MA(VAR1, timeperiod=5)
    #VAR3 = ta.MA(VAR2,timeperiod=8)  

    length = -100
    fig = plt.figure()
    ax = fig.add_subplot(111)
    raw_data['time'] = raw_data['date'].map(date2num)
    data = DataFrame(raw_data, columns=['time', 'open','close','high','low'])
    data = np.array(data)
    candlestick_ochl(ax,data[length:],width=0.6,colordown=u'g',colorup=u'r')

    plt.grid()
    plt.plot(raw_data['date'][length:], H1[length:],color='r',label='H1')
    #plt.plot(raw_data['date'][length:], H3[length:],color='y',label='H3')
    #plt.plot(raw_data['date'][length:], H5[length:],color='k',label='H3')
    plt.plot(raw_data['date'][length:], H2[length:], color='g',label='H2')     #没能解决中间周六周天节假日数据问题
    plt.show()


draw_tianbijun('000656')

def draw_rzye():
    data = ts.sh_margins(start='2015-06-20', end='2015-10-28')
    data['opDate'] = data['opDate'].map(str2date2)
    data = data.sort_index(ascending=True)
    data['rzye'] = data['rzye']/100000000
    data['rzmre'] = data['rzmre']/10000000
    data['rqyl'] = data['rqyl']/1000000
    data['rqmcl'] = data['rqmcl']/1000000
    length = -200
    plt.plot(data['opDate'][length:],data['rzye'][length:],'r',label='rzye')
    plt.plot(data['opDate'][length:],data['rzmre'][length:],'g',label='rzmre')
    plt.show()


