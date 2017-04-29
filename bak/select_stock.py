# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20151026
import tushare as ts
from download import DownLoad
from datetime import datetime

class StockInfo(object):
    def __init__(self, stock):
        self.dl = DownLoad()

    def reference_info(self, stock):
        data = ts.profit_data(top=60)
        data.sort('shares',ascending=False)
        print data[data.shares>=10]

    def forcast_data(self,stock):
        data = ts.forecast_data(2015,3)
        print data[-100:]

    def new_stock(self, stock):
        pass

    def margin_trading(self, stock):
        today = datetime.today().strftime("%Y-%m-%d")
        data = ts.sh_margins(start='2015-08-20', end=today)
if __name__ == '__main__':
    data = ts.sh_margins(start='2015-10-20', end='2015-10-28')
    data['rzye'] = data['rzye']/100000000
    data['rzmre'] = data['rzmre']/100000000
    data['rqyl'] = data['rqyl']/1000000
    data['rqmcl'] = data['rqmcl']/1000000

    
