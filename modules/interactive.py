# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

import sys
import json
import time
import socket
import platform
import datetime
import threading
from paramiko.py3compat import u
from models import models
from modules.db_conn import redis_log

log_2_redis = "audit_log"
os_type = platform.system()
if os_type == "Windows":
    has_termios = False
elif os_type == "Linux":
    import termios  # windows does not have termios...
    import tty
    has_termios = True
else:
    print("system/OS name is:", os_type)


def interactive_shell(chan, user_obj, bind_host_obj, log_recording):
    """
    :param chan: interactive shell
    :param user_obj: object of login user
    :param bind_host_obj: object of login host
    :param log_recording: log_recording func
    :return:
    """
    if has_termios:
        posix_shell(chan, user_obj, bind_host_obj, log_recording)
    else:
        windows_shell(chan, user_obj, bind_host_obj, log_recording)


def posix_shell(chan, user_obj, bind_host_obj, log_recording):
    import select
    oldtty = termios.tcgetattr(sys.stdin)  # 获取终端属性

    write_log = threading.Thread(target=write_logs, args=(user_obj, bind_host_obj, log_recording,))
    write_log.start()

    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)
        cmd = ''

        tab_key = False
        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])  # 监听管道及标准输入
            if chan in r:  # 管道中有数据, 用户指令或者执行指令结果
                try:
                    x = u(chan.recv(1024))
                    if tab_key:
                        if x not in ('\x07', '\r\n'):
                            # print('tab:',x)
                            cmd += x
                        tab_key = False
                    if len(x) == 0:
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:  # 读取标准输入(用户输入指令)
                x = sys.stdin.read(1)
                if '\r' != x:
                    cmd += x
                else:  # "\r" 用户按了"Enter"键,指令结束
                    print('cmd->:', cmd)
                    log_dic = dict(action_type='cmd', cmd=cmd,
                                   date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    dic_2_json = json.dumps(log_dic)
                    redis_log.lpush(log_2_redis, dic_2_json)

                if '\t' == x:
                    tab_key = True
                if len(x) == 0:
                    break
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)  # 重置终端属性


# thanks to Mike Looijmans for this code
def windows_shell(chan, user_obj, bind_host_obj, log_recording):

    sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

    def writeall(sock):
        while True:  # 等待接收数据(用户输入或者命令返回结果)
            data = sock.recv(256)
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data.decode())
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()
    write_log = threading.Thread(target=write_logs, args=(user_obj, bind_host_obj, log_recording,))
    write_log.start()

    try:
        cmd = ""
        while True:
            d = sys.stdin.read(1)  # 读取标准输入(用户输入指令)
            if not d:
                break

            if d.endswith("\n"):  # 读取到"\n"(包含"\r\n")时, 用户按下了回车键"Enter",输入指令结束
                log_dic = dict(action_type='cmd',
                               cmd=cmd,
                               date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                dic_2_json = json.dumps(log_dic)
                redis_log.lpush(log_2_redis, dic_2_json)
                cmd = ""
            else:
                cmd += d
            chan.send(d)  # 向chan管道发送指令
    except EOFError:
        # user hit ^Z or F6
        pass


def write_logs(user_obj, bind_host_obj, log_recording):
    while True:
        item = redis_log.brpop(log_2_redis, 1)  # 如果"log_2_redis"中没有数据, 等待1秒
        if item:
            json_2_dic = json.loads(item[1].decode(), encoding="utf-8")
            log_item = models.AuditLog(user_id=user_obj.id,
                                       bind_host_id=bind_host_obj.id,
                                       action_type=json_2_dic.get("action_type", "cmd"),
                                       cmd=json_2_dic.get("cmd", None),
                                       date=json_2_dic.get("date", None)
                                       )
            log_recording(log_item)

