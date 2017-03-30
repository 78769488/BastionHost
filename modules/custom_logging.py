#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
logging配置
"""

import logging.config
import os

from conf import settings

BASE_DIR = settings.BASE_DIR

logfile_path = os.path.join(BASE_DIR, 'log')
if not logfile_path:
    os.makedirs(logfile_path)

# log文件的全路径
LOGFILE_ALL = os.path.join(logfile_path, 'all.log')
LOGFILE_ERR = os.path.join(logfile_path, 'err.log')

level_console = settings.LEVEL_CONSOLE if settings.LEVEL_CONSOLE else 'DEBUG'
level_files = settings.LEVEL_FILES if settings.LEVEL_FILES else 'INFO'


# 定义三种日志格式
standard_format = '[%(asctime)s]-[%(threadName)s:%(thread)d]-[task_id:%(name)s]-[%(filename)s:%(lineno)d]' \
                  '-[%(levelname)s]: %(message)s'
# simple_format = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]: %(message)s'
simple_format = '[%(asctime)s-%(filename)s:%(lineno)d]] %(message)s'

# log配置字典
logging_dic = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': standard_format
        },
        'simple': {
            'format': simple_format
        },
    },
    'filters': {},
    'handlers': {
        'console': {
            'level': level_console,
            'class': 'logging.StreamHandler',  # 打印到屏幕
            'formatter': 'simple'
        },
        'default': {
            'level': level_files,
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
            'filename': LOGFILE_ALL,  # 日志文件
            'maxBytes': 1024*1024*5,  # 日志大小 5M
            'backupCount': 50,
            'formatter': 'standard',
            'encoding': 'utf-8',

        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
            'filename': LOGFILE_ERR,  # 日志文件
            'maxBytes': 1024*1024*5,  # 日志大小 5M
            'backupCount': 50,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
    'loggers': {
        '': {
            'handlers': ['default', 'console', 'error'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
logging.config.dictConfig(logging_dic)  # 导入上面定义的配置

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info('It works!')  # 记录该文件的运行状态
