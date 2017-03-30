#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhangrf
# E-mail: 78769488@qq.com
# Create: 2017/3/30

import sys
from conf import settings

BASE_DIR = settings.BASE_DIR
print(BASE_DIR)
sys.path.append(BASE_DIR)

if __name__ == '__main__':
    from modules.actions import excute_from_command_line
    excute_from_command_line(sys.argv)
