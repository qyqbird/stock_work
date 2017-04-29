# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 2014-04-14

class NoInstance(type):
    def __call__(self, *args, **kwargs):
        raise TypeError("工具类 can't instantiate directly")

class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super(Singleton,self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super(Singleton,self).__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance

