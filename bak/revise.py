# -*- coding: utf-8 -*-
# @Author: yuqing5
import copy

buy_amount = [250, 650, 1850, 5800]
read_amount = [780, 1287, 3581, 10000]

buy_amount1 = [200, 600, 2000, 20000]
read_amount1 = [340, 840, 3000, 31000]

def revise(read_amount, buy_amount):
    ratio = []
    for i in range(len(read_amount)):   
        bizhi = float(read_amount[i]) / float(buy_amount[i])
        ratio.append(bizhi)
    sorted_ratio = sorted(ratio)
    search_ratio = copy.deepcopy(ratio)

    #寻找最小比值，固定该值
    position_0 = find_idx(search_ratio, sorted_ratio[0])
    if position_0 == 0:
        position_1 = find_idx(search_ratio, sorted_ratio[1])
        if position_1 == 1:    #次小值在第二位,1 2 x y
            position_2 = find_idx(search_ratio, sorted_ratio[2])
            if position_2 == 3: #1, 2, 4, 3情况
                corr2 = ratio[1] + (ratio[3] - ratio[1])* 0.5
                read_amount[2] = buy_amount[2] * corr2
        elif position_1 == 2:   #次小值在第三位,修改第二个值 1, x, 2, y
            corr1 = ratio[0] + (ratio[2] - ratio[0]) * 0.5
            read_amount[1] = buy_amount[1] * corr1
        else:
            #1,x,y,2
            corr1 = ratio[0] + (ratio[3] - ratio[0])* 0.33
            corr2 = ratio[0] + (ratio[3] - ratio[0])* 0.67
            read_amount[1] = buy_amount[1] * corr1
            read_amount[2] = buy_amount[2] * corr2


    #寻找次小值进行改变
    if position_0 == 1:     #x, 1 ,y,z,先修正x
        corr0 = 1 + (ratio[1] - 1)* 0.8
        read_amount[0] = buy_amount[0] * corr0
        position_1 = find_idx(search_ratio, sorted_ratio[1])
        if position_1 == 0: #2 1 x y
            position_2 = find_idx(search_ratio, sorted_ratio[2])
            if position_2 == 3: # 2 1 4 3
                corr2 = ratio[1] + (ratio[3] - ratio[1])* 0.5
                read_amount[2] = buy_amount[2] * corr2
            # 2 1 3 4
        elif position_1 == 3:   # x 1 y 2
            corr2 = ratio[1] + (ratio[3] - ratio[1])* 0.5
            read_amount[2] = buy_amount[2] * corr2

    if position_0 == 2:     #x, y 1 z 
        corr0 = 1.0 + (ratio[2] - 1.0)* 0.5
        corr1 = 1.0 + (ratio[2] - 1.0)* 0.75
        read_amount[0] = buy_amount[0] * corr0
        read_amount[1] = buy_amount[1] * corr1        

    if position_0 == 3:     # x y z 1
        corr0 = 1.0 + (ratio[3] - 1.0)* 0.5
        corr1 = 1.0 + (ratio[3] - 1.0)* 0.67
        corr2 = 1.0 + (ratio[3] - 1.0)* 0.8
        read_amount[0] = buy_amount[0] * corr0
        read_amount[1] = buy_amount[1] * corr1
        read_amount[2] = buy_amount[2] * corr2

    print read_amount

def find_idx(ratio, value):
    for i in range(len(ratio)):
        if value == ratio[i]:
            ratio[i] = 0 #防止遇到相同ratio的问题，一直返回同一个值
            return i


#测试算法
def test():
    buy = [10, 100 ,1000, 10000]    #固定住

    read_1 = [10, 100, 1000, 10000]   #出现相同的比值
    read_2 = [15, 160, 1700, 18000]   #1 2 3 4
    read_3 = [15, 160, 1800, 17000]   #1 2 4 3
    read_4 = [15, 180, 1600, 17000]   #1 x 2 y
    read_5 = [15, 180, 1800, 17000]   #1 x y 2
    read_6 = [16, 150, 1800, 17000]   #2 1 4 3
    read_7 = [17, 150, 1800, 16000]   #x 1 y 2
    read_8 = [17, 160, 1500, 16000]   #x y 1 z
    read_9 = [17, 180, 1800, 16000]   #x y z 1
    revise(read_1, buy)
    revise(read_2, buy)
    revise(read_3, buy)
    revise(read_4, buy)
    revise(read_5, buy)
    revise(read_6, buy)
    revise(read_7, buy)
    revise(read_8, buy)
    revise(read_9, buy)


test()








