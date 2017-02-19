# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20160416

'''
每天临晨更新数据到mysql
以及缓存数据
'''
from stock_select.foundmental import StockSelect
from utility.download import TS,DownLoad
import datetime
def update():
    print "start update:".format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
    #1. 
    StockSelect()
    #2. 
    dl = DownLoad()
    dl.update_everyday()
    print "END UPDATE:".format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))




if __name__ == '__main__':
    update()
