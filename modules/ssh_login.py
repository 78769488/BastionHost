#!/usr/bin/env python
# -*- coding=utf-8 -*-

import base64
import getpass
import os
import socket
import sys
import traceback
from paramiko.py3compat import input
from models import models
# from modules.db_conn import engine
import datetime

import paramiko
try:
    import interactive
except ImportError:
    from . import interactive


def ssh_login(user_obj, bind_host_obj, mysql_engine, log_recording):
    # now, connect and use paramiko Client to negotiate SSH2 across the connection
    try:
        client = paramiko.SSHClient()  # create SSHClient object
        client.load_system_host_keys()  # 加载用户的.ssh密钥文件
        client.set_missing_host_key_policy(paramiko.WarningPolicy())  # 允许连接不在know_hosts文件中的主机
        print('*** Connecting...')
        # client.connect(hostname, port, username, password)
        client.connect(bind_host_obj.host.ip,
                       bind_host_obj.host.port,
                       bind_host_obj.remote_user.username,
                       bind_host_obj.remote_user.password,
                       timeout=30)

        # cmd_caches = []
        chan = client.invoke_shell()  # Start an interactive shell session on the SSH server.
        print(repr(client.get_transport()))
        print('*** Here we go!\n')
        log_item = models.AuditLog(user_id=user_obj.id,
                                  bind_host_id=bind_host_obj.id,
                                  action_type='login',
                                  date=datetime.datetime.now()
                                  )  # 设定AuditLog表中各字段值
        log_recording(log_item)
        interactive.interactive_shell(chan, user_obj, bind_host_obj, log_recording)
        chan.close()
        client.close()

    except Exception as e:
        print('*** Caught exception: %s: %s' % (e.__class__, e))
        traceback.print_exc()
        try:
            client.close()
        except:
            pass
        sys.exit(1)
