#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhangrf
# E-mail: 78769488@qq.com
# Create: 2017/3/30

import os

DB_CONN = "mysql+pymysql://root:bewinner@127.0.0.1/bastion_host?charset=utf8"
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

# 打印到屏幕的日志级别
LEVEL_CONSOLE = "DEBUG"

# 保存到文件的日志级别
LEVEL_FILES = 'DEBUG'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')  # 数据文件目录
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR)

if __name__ == '__main__':
    print(BASE_DIR)
