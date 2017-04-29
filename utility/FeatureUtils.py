#-*- coding:utf-8 -*-
#Date:2017-02-22
#Author:yuqing.qin
#desc:特征处理类

import pandas as pd
from collections import Counter

def bins(filename, columns, feature_nums=50):
    rawdata = pd.read_table(filename,header=None,sep='\t')
    #等频离散,借助np里面的一些工具
    data = list(rawdata[columns])
    counter = Counter(data)
    min_value = min(data)
    max_value = max(data)
    counter = sorted(counter.iteritems(),key=lambda pair:pair[0])
    accumu_counter = np.cumsum([item[1] for item in counter])        
    sum_count = float(accumu_counter[len(accumu_counter) - 1])
    assert sum_count == len(data)

    bin_nums
    feature_idx = 1
    interval_dict = {}
    interval_list = []
    for idx in xrange(0, len(accumu_counter)):
        theory_value = (sum_count / bin_nums) * feature_idx
        if accumu_counter[idx] < theory_value and accumu_counter[idx+1] < theory_value:
            continue
        if accumu_counter[idx] >= theory_value or (theory_value - accumu_counter[idx]) < (accumu_counter[idx+1]-theory_value):
            interval_dict[feature_idx] = [min_value, counter[idx][0]]
            min_value = counter[idx][0]
            feature_idx += 1
            if feature_idx == feature_nums:
                interval_dict[feature_idx] = [min_value, max_value]
                break;
    return interval_dict

def get_feature_name(columns_name, feature_interval, value):
    for idx, interval in feature_interval.iteritems():
        if interval[0] <= value <= interval[1]:
            return columns_name + "_" + str(interval[0]) + "_" + str(interval[1])
    high = len(feature_interval)
    if feature_interval[high][1] < value:
        print "warn beyond high margin", columns_name, value
        return column_name +"_" + str(feature_interval[high][0]) + "_" +str(feature_interval[high][1])
    else:
        print "Warn, beyond low margin",column_name, value
        return column_name +"_" + str(feature_interval[1][0]) + "_" +str(feature_interval[1][1])


