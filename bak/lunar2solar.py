#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20151015
#import tushare as ts

import datetime
solar_month_day = [0,31,28,31,30,31,30,31,31,30,31,30,31]
LUNAR_CALENDAR_TABLE = [  
0x04AE53,0x0A5748,0x5526BD,0x0D2650,0x0D9544,0x46AAB9,0x056A4D,0x09AD42,0x24AEB6,0x04AE4A, # //*1901-1910*/  
0x6A4DBE,0x0A4D52,0x0D2546,0x5D52BA,0x0B544E,0x0D6A43,0x296D37,0x095B4B,0x749BC1,0x049754, # //*1911-1920*/  
0x0A4B48,0x5B25BC,0x06A550,0x06D445,0x4ADAB8,0x02B64D,0x095742,0x2497B7,0x04974A,0x664B3E, # //*1921-1930*/  
0x0D4A51,0x0EA546,0x56D4BA,0x05AD4E,0x02B644,0x393738,0x092E4B,0x7C96BF,0x0C9553,0x0D4A48, # //*1931-1940*/     
0x6DA53B,0x0B554F,0x056A45,0x4AADB9,0x025D4D,0x092D42,0x2C95B6,0x0A954A,0x7B4ABD,0x06CA51, # //*1941-1950*/  
0x0B5546,0x555ABB,0x04DA4E,0x0A5B43,0x352BB8,0x052B4C,0x8A953F,0x0E9552,0x06AA48,0x6AD53C, # //*1951-1960*/  
0x0AB54F,0x04B645,0x4A5739,0x0A574D,0x052642,0x3E9335,0x0D9549,0x75AABE,0x056A51,0x096D46, # //*1961-1970*/  
0x54AEBB,0x04AD4F,0x0A4D43,0x4D26B7,0x0D254B,0x8D52BF,0x0B5452,0x0B6A47,0x696D3C,0x095B50, # //*1971-1980*/  
0x049B45,0x4A4BB9,0x0A4B4D,0xAB25C2,0x06A554,0x06D449,0x6ADA3D,0x0AB651,0x093746,0x5497BB, # //*1981-1990*/  
0x04974F,0x064B44,0x36A537,0x0EA54A,0x86B2BF,0x05AC53,0x0AB647,0x5936BC,0x092E50,0x0C9645, # //*1991-2000*/  
0x4D4AB8,0x0D4A4C,0x0DA541,0x25AAB6,0x056A49,0x7AADBD,0x025D52,0x092D47,0x5C95BA,0x0A954E, # //*2001-2010*/  
0x0B4A43,0x4B5537,0x0AD54A,0x955ABF,0x04BA53,0x0A5B48,0x652BBC,0x052B50,0x0A9345,0x474AB9, # //*2011-2020*/  
0x06AA4C,0x0AD541,0x24DAB6,0x04B64A,0x69573D,0x0A4E51,0x0D2646,0x5E933A,0x0D534D,0x05AA43, # //*2021-2030*/  
0x36B537,0x096D4B,0xB4AEBF,0x04AD53,0x0A4D48,0x6D25BC,0x0D254F,0x0D5244,0x5DAA38,0x0B5A4C, # //*2031-2040*/  
0x056D41,0x24ADB6,0x049B4A,0x7A4BBE,0x0A4B51,0x0AA546,0x5B52BA,0x06D24E,0x0ADA42,0x355B37, # //*2041-2050*/  
0x09374B,0x8497C1,0x049753,0x064B48,0x66A53C,0x0EA54F,0x06B244,0x4AB638,0x0AAE4C,0x092E42, # //*2051-2060*/  
0x3C9735,0x0C9649,0x7D4ABD,0x0D4A51,0x0DA545,0x55AABA,0x056A4E,0x0A6D43,0x452EB7,0x052D4B, # //*2061-2070*/  
0x8A95BF,0x0A9553,0x0B4A47,0x6B553B,0x0AD54F,0x055A45,0x4A5D38,0x0A5B4C,0x052B42,0x3A93B6, # //*2071-2080*/  
0x069349,0x7729BD,0x06AA51,0x0AD546,0x54DABA,0x04B64E,0x0A5743,0x452738,0x0D264A,0x8E933E, # //*2081-2090*/  
0x0D5252,0x0DAA47,0x66B53B,0x056D4F,0x04AE45,0x4A4EB9,0x0A4D4C,0x0D1541,0x2D92B5           # //*2091-2099*/  
]

def year_days(year):
    '''
    针对阳历
    判断year是否闰年
    '''
    if year % 400 == 0:
        return 366

    if year%4==0 and year%100!=0:
        return 366

    return 365

def get_month_day(year, month):
    days = solar_month_day[month]
    if (year%4 == 0 and year%100!= 0) or (year%400 == 0):
        if month == 2:
            days += 1
    return days
def is_leap_month(year, month):
    '''
    判断是否闰月
    针对阴历
    '''
    leap_month = (LUNAR_CALENDAR_TABLE[year-1901] >> 20) & 0xF  # 为0表示无闰月
    if leap_month!=0 and leap_month==month:
        return True
    else:
        return False

def days_past(year, month, day):
    '''
    返回给定日期在全年第几天
    '''
    days = day
    for idx in range(1, month):
        days += get_month_day(year, month)
    return days

def lunar_days_past(year, month, day，is_leap_month):
    lunar_days  = 0
    lmonth_index = lday_index = 1    # 农历月份，日期遍历索引
    leap_month_days = 0    # 暂存闰月前月的天数
    bits = 19   # 遍历获取大小月索引, 大月:1, 小月:0

    for idx in range(1, 14): 
        big_month_flag = (LUNAR_CALENDAR_TABLE[year-1901] >> bits) & 0x1

        #如果当前月份<指定月数，加起来
        if idx < month:
            lunar_days  += 29 + big_month_flag

        if is_leap_month(year, lmonth_index):
            leap_month_days = 29 + l_big_month    　 #暂存当前月(其下月为闰月)天数

        if is_leap_month(year, lmonth_index - 1):
            if lmonth_index - 1 == lmonth and is_leap_month:
                lunar_days += leap_month_days
                break

            if lmonth_index == lmonth:
                lunar_days += 29 + l_big_month
                break

            if lmonth_index - 1 < lmonth and lmonth_index != lmonth:
                lmonth += 1

        bits -= 1
    lunar_days += lday
    return lunar_days

# 根据计算处理的天数间隔和年份，求阳历月和日
def get_solar_month_day(syear, solar_days_to_calculate):
    smonth = 1
    while solar_days_to_calculate - get_syear_total_month_days(syear, smonth) > 0:
        solar_days_to_calculate -= get_syear_total_month_days(syear, smonth)
        smonth += 1
    sday = solar_days_to_calculate
    return (smonth, sday)


# 根据给定农历年月日及是否闰月求阳历年月日
def trans_lular2_solar(lyear, lmonth, lday, is_leap_month=False):
    is_leap_month &= is_leap_month(lyear, lmonth)　　# 判断是否闰月
    lunar_days = lunar_days_past(lyear, lmonth, lday, is_leap_month)    # 正月初一至当前农历日期天数间隔    

    #获取当前农历年份正月初一所在阳历日期
    spring_month = (LUNAR_CALENDAR_TABLE[lyear - 1901] & 0x60) >> 5           
    spring_day = spring_day = LUNAR_CALENDAR_TABLE[lyear - 1901] & 0x1F    
    solar_days_to_spring_day = days_past(lyear, spring_month, spring_day)  # 从阳历１月１日至正月初一阳历日期的时间间隔

    solar_days_to_calculate = solar_days_to_lday = solar_days_to_spring_day + lunar_days - 1
    total_solar_year_days = year_days(lyear)    # 365 or 366

    syear = lyear    # 阳历日期
    #如果阳历年已翻年
    if solar_days_to_lday > total_solar_year_days:
        solar_days_to_calculate = solar_days_to_lday - total_solar_year_days
        syear += 1    # 阳历年+1

    smonth, sday = get_solar_month_day(syear, solar_days_to_calculate)

    return {'year':syear, 'month':smonth, 'day':sday}


trans_lular2_solar