#-*- coding:utf-8 -*-
#Date:20167-02-18
#Author:yuqing.qin
#desc:收集新股涨停数据，训练模型

import tushare as ts

shanghai = ts.get_k_data('000001',index=True)
shanghai.index = shanghai['date']
shenzheng = ts.get_k_data('399001',index=True)
shenzheng.index = shenzheng['date']

def get_market_info(today, yesterday, market):
    today_close = market.ix[today]['close']
    yester_close = market.ix[yesterday]['close']
    return (today_close - yester_close) / yester_close * 100



def get_train_data(filename):
    rawdata = ts.get_stock_basics()
    fo = open(filename,'w')

    for code in rawdata.index:
        timeToMarket = rawdata.ix[code]['timeToMarket']
        if timeToMarket < 20150101:
            continue
        k_tickt = ts.get_k_data(code)
        size = 30
        if len(k_tickt.index) < 3:
            continue
        elif len(k_tickt.index) < 30:
            size = len(k_tickt.index)
        #计算涨停板个数
        winners = 1
        for x in xrange(1,size):
            today_close = k_tickt.ix[x]['close']
            yester_close = k_tickt.ix[x-1]['close']
            ratio = (today_close - yester_close) / yester_close
            tradeday = k_tickt.ix[x]['date']
            tradeyesterday = k_tickt.ix[x-1]['date']

            shanghaiFeature = get_market_info(tradeday, tradeyesterday, shanghai)
            shenzhengFeature = get_market_info(tradeday, tradeyesterday, shenzheng)
            Feature = [code]
            Feature.extend(rawdata.ix[code])  #这里面的PE等参数随着股价的变化，其实是变的
            Feature.append(yester_close)
            Feature.append(winners)
            Feature = [str(item) for item in Feature]
            #还有昨天涨幅特征，累计涨幅特征，最近一个星期涨幅特征，两个星期累计特征
            if ratio >= 0.097:
                fo.write("1\t" + '\t'.join(Feature) + '\n')
                winners += 1
            else:
                #开板后一段时间就可以放弃了
                # 是每天的涨停都算一个记录，还是破板的时候才算一个记录
                if x < winners * 2:
                    fo.write("0\t" + '\t'.join(Feature) + '\n')
                else:
                    break

    fo.close()

if __name__ == '__main__':
    get_train_data('rawData')
