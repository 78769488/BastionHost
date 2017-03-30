#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhangrf
# E-mail: 78769488@qq.com
# Create: 2017/3/30

from conf import action_registers
from modules import utils


def help_msg():
    """
    print help msgs
    :return:
    """
    print("\033[31;1mAvailable commands:\033[0m")
    for key in action_registers.actions:
        print("\t", key)


def excute_from_command_line(argvs):  # python bastion_host [argvs]
    if len(argvs) < 2:  # 没有带参数运行
        help_msg()
        exit()
    if argvs[1] not in action_registers.actions:  # 错误的命令参数
        utils.print_err("Command [%s] does not exist!" % argvs[1], logout=True)
    action_registers.actions[argvs[1]](argvs[1:])
