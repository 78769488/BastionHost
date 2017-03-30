#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhangrf
# E-mail: 78769488@qq.com
# Create: 2017/3/30

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def print_err(msg, logout=False):
    output = "\033[31;1mError: %s\033[0m" % msg
    if logout:
        exit(output)
    else:
        print(output)


def yaml_parser(yml_filename):
    """
    load yaml file and return
    :param yml_filename:
    :return:
    """
    # yml_filename = "%s/%s.yml" % (settings.StateFileBaseDir,yml_filename)
    try:
        yaml_file = open(yml_filename,'r')
        data = yaml.load(yaml_file)
        return data
    except Exception as e:
        print_err(e)
