# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20160502
'''
计算定投收益
'''
from utility.download import TS,DownLoad

MONEY = 10000   #每个月定投10000，选择定投时间月底
def compute_earn(raw_data, expect=1.5, start=1):
    '''
    预期收益50%，已经算比较高的了
    '''
    residu_money, shares = 0, 0
    shares = int(10000/raw_data[start-1])
    residu_money = 10000 - shares * raw_data[start-1]
    for index, item in enumerate(raw_data[start:], start=2):
        #1. 先检查是否已经达到收益率预期了
        current = residu_money + shares * item
        current_earn = current/(MONEY*(index-1))
        total = (index-1)* MONEY
        if current_earn > expect:
            print "用时{0}月,投资{1}，当前价值{2} 收益{3:.1%} 止盈".format(index,total, current,current_earn)
            print 'Congratulations'
            break
        else:
            print "截止{0}月,投资{1}，当前价值{2} 收益{3:.1%},继续".format(index,total, current,current_earn)
            residu_money += MONEY
            #快达到目标时，不在定投了
            if current_earn < expect*0.9:
                share = int(residu_money/item)
                shares += share
                residu_money -= share * item


def test_stock():
    dl = DownLoad()
    data = dl.load_data('600303')
    data.index = data['date']
    data = data.asfreq('M',method='ffill')
    compute_earn(data['close'], start=10)


test_stock()