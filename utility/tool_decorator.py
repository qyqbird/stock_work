# -*- coding: utf-8 -*-
# @Author: yuqing5
# date: 20160410
import datetime
import time
import os
import cPickle
import functools
from functools import partial
import logging

'''
缓存文件装饰器
'''
def local_memcached(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        today = time.strftime("%Y%m%d",time.localtime())
        file_name = '/root/stock_work/stock_select/local_mem_data/'+args[1] + '_' + today
        result = None
        if os.path.exists(file_name):
            #print 'load local:{0}'.format(file_name)
            result =  cPickle.load(file(file_name))
        else:
            #result = func(*args, **kw)
            #如果有额外的参数
            if len(args) > 2:
                result = args[0](*(args[2:]), **kw)
            else:
                result = args[0](**kw)
            cPickle.dump(result, file(file_name,'w'))
            #print '\nload internet and memcached:{0}'.format(file_name)
        return result
    return wrapper


def running_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start_time = datetime.datetime.now()
        ret = func(*args, **kw)
        end_time = datetime.datetime.now()
        print '[%s()] done, run time : %r sec' % (func.__name__, (end_time - start_time).seconds)
        return ret
    return wrapper



#可自定义属性的装饰器
def attach_wrapper(obj, func=None):
    if func is None:
        return partial(attach_wrapper, obj)
    setattr(obj, func.__name__, func)
    return func

#日志装饰器
def logged(level, name=None, message=None):
    '''
    Add logging to a function. level is the logging
    level, name is the logger name, and message is the
    log message. If name and message aren't specified,
    they default to the function's module and name.
    '''
    def decorator(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log.log(level, logmsg)
            return func(*args, **kwargs)

#nolocal 是python3的新东西
        # @attach_wrapper(wrapper)
        # def set_level(newlevel):
        #     nolocal level
        #     level = newlevel

        # @attach_wrapper(wrapper)
        # def set_message(newmessage):
        #     nolocal message
        #     message = newmessage
        return wrapper

    return decorator


