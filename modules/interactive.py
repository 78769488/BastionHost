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
import time
import socket
import datetime
from paramiko.py3compat import u
from models import models

# windows does not have termios...
try:
    import termios
    import tty

    has_termios = True
except ImportError as e:
    print(e)
    has_termios = False


def interactive_shell(chan, user_obj, bind_host_obj, cmd_caches, log_recording):
    """
    :param chan: interactive shell
    :param user_obj: object of login user
    :param bind_host_obj: object of login host
    :param cmd_caches: argvs for write to audit_log table
    :param log_recording: log_recording func
    :return:
    """
    if has_termios:
        posix_shell(chan, user_obj, bind_host_obj, cmd_caches, log_recording)
    else:
        windows_shell(chan, user_obj, bind_host_obj, cmd_caches, log_recording)


def posix_shell(chan, user_obj, bind_host_obj, cmd_caches, log_recording):
    import select
    t1 = time.time()
    oldtty = termios.tcgetattr(sys.stdin)  # 获取终端属性
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
                    log_item = models.AuditLog(user_id=user_obj.id,
                                               bind_host_id=bind_host_obj.id,
                                               action_type='cmd',
                                               cmd=cmd,
                                               date=datetime.datetime.now()
                                               )
                    cmd_caches.append(log_item)
                    cmd = ''

                    if len(cmd_caches) >= 10:
                        log_recording(user_obj, bind_host_obj, cmd_caches)
                        cmd_caches = []
                        t1 = time.time()

                    elif len(cmd_caches) >= 1:
                        t2 = time.time()
                        if t2 - t1 > 60:  # 如果超过程60秒, 指令队列中仍然有数据, 就写数据库,
                            log_recording(user_obj, bind_host_obj, cmd_caches)
                            cmd_caches = []
                            t1 = time.time()

                if '\t' == x:
                    tab_key = True
                if len(x) == 0:
                    break
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)  # 重置终端属性


# thanks to Mike Looijmans for this code
def windows_shell(chan, user_obj, bind_host_obj, cmd_caches, log_recording):
    import threading
    t1 = time.time()  # 记录当前时间

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

    try:
        cmd = ""
        while True:
            d = sys.stdin.read(1)  # 读取标准输入(用户输入指令)
            if not d:
                break

            if d.endswith("\n"):  # 读取到"\n"(包含"\r\n")时, 用户按下了回车键"Enter",输入指令结束
                print("cmd--->:", cmd)
                log_item = models.AuditLog(user_id=user_obj.id,
                                           bind_host_id=bind_host_obj.id,
                                           action_type='cmd',
                                           cmd=cmd,
                                           date=datetime.datetime.now()
                                           )
                cmd_caches.append(log_item)
                cmd = ""

                if len(cmd_caches) >= 10:
                    log_recording(user_obj, bind_host_obj, cmd_caches)
                    cmd_caches = []
                    t1 = time.time()

                elif len(cmd_caches) >= 1:
                    t2 = time.time()
                    if t2 - t1 > 60:  # 如果超过程60秒, 指令队列中仍然有数据, 就写数据库,
                        log_recording(user_obj, bind_host_obj, cmd_caches)
                        cmd_caches = []
                        t1 = time.time()

            else:
                cmd += d
            chan.send(d)  # 向chan管道发送指令
    except EOFError:
        # user hit ^Z or F6
        pass
