#!/usr/bin/env python
# -*- coding=utf-8 -*-

import logging
from modules import custom_logging
from models import models
from conf import settings
from modules.utils import print_err, yaml_parser
from modules.db_conn import engine, session
from modules import ssh_login

logger = logging.getLogger(__name__)


def syncdb(argvs):
    print("Syncing DB....")
    try:
        models.Base.metadata.create_all(engine)  # 创建所有表结构
        logger.info("create tables sucess!")
    except Exception as e:
        logger.error(e)


def create_hosts(argvs):
    """
    create hosts
    :param argvs:
    :return:
    """
    if '-f' in argvs:
        hosts_file = argvs[argvs.index("-f") + 1]
    else:
        print_err("invalid usage, should be:\ncreate_hosts -f <the new hosts file>", logout=True)
        return
    source = yaml_parser(hosts_file)
    if source:
        logger.debug("source:\n%s" % source)
        for key, val in source.items():
            logger.debug("%s:%s" % (key, val))
            obj = models.Host(hostname=key, ip=val.get('ip'), port=val.get('port') or 22)
            logger.info(obj)
            session.add(obj)
        session.commit()
        logger.info("create hosts sucess!")


def create_remoteusers(argvs):
    """
    create remoteusers
    :param argvs:
    :return:
    """
    if '-f' in argvs:
        remoteusers_file = argvs[argvs.index("-f") + 1]
    else:
        print_err("invalid usage, should be:\ncreate_remoteusers -f <the new remoteusers file>", logout=True)
        return
    source = yaml_parser(remoteusers_file)
    if source:
        logger.debug("source:\n%s" % source)
        for key, val in source.items():
            logger.debug("%s:%s" % (key, val))
            obj = models.RemoteUser(username=val.get('username'),
                                    auth_type=val.get('auth_type'),
                                    password=val.get('password'))
            logger.info(obj)
            session.add(obj)
        session.commit()
        logger.info("create remoteusers sucess!")


def create_users(argvs):
    """
    create user
    :param argvs:
    :return:
    """
    if '-f' in argvs:
        user_file = argvs[argvs.index("-f") + 1]
    else:
        print_err("invalid usage, should be:\ncreateusers -f <the new users file>", logout=True)
        return

    source = yaml_parser(user_file)
    if source:
        logger.debug("source:\n%s" % source)
        for key, val in source.items():
            logger.debug("%s:%s" % (key, val))
            obj = models.UserProfile(username=key, password=val.get('password'))
            logger.info(obj)
            # if val.get('groups'):
            #     groups = session.query(models.Group).filter(models.Group.name.in_(val.get('groups'))).all()
            #     if not groups:
            #         print_err("none of [%s] exist in group table." % val.get('groups'),quit=True)
            #     obj.groups = groups
            # if val.get('bind_hosts'):
            #     bind_hosts = common_filters.bind_hosts_filter(val)
            #     obj.bind_hosts = bind_hosts
            # print(obj)
            session.add(obj)
        session.commit()
        logger.info("create user sucess!")


def create_groups(argvs):
    """
    create groups
    :param argvs:
    :return:
    """
    if '-f' in argvs:
        group_file = argvs[argvs.index("-f") + 1]
    else:
        print_err("invalid usage, should be:\ncreategroups -f <the new groups file>", logout=True)
        return
    source = yaml_parser(group_file)
    if source:
        logger.debug("source:\n%s" % source)
        for key, val in source.items():
            logger.debug("%s:%s" % (key, val))
            obj = models.HostGroup(name=key)
            logger.info(obj)
            # 简化.yaml数据结构,复杂关联关系单独处理
            # if val.get('bind_hosts'):
            #     bind_hosts = common_filters.bind_hosts_filter(val)
            #     obj.bind_hosts = bind_hosts
            #
            # if val.get('user_profiles'):
            #     user_profiles = common_filters.user_profiles_filter(val)
            #     obj.user_profiles = user_profiles
            session.add(obj)
        session.commit()
        logger.info("create groups sucess!")


def create_bindhosts(argvs):
    """
    create bind hosts
    主机及该主机上的账户信息
    :param argvs:
    :return:
    """
    if '-f' in argvs:
        bindhosts_file = argvs[argvs.index("-f") + 1]
    else:
        print_err("invalid usage, should be:\ncreate_bindhosts -f <the new bindhosts file>", logout=True)
        return
    source = yaml_parser(bindhosts_file)
    if source:
        logger.debug("source:\n%s" % source)
        for key, val in source.items():
            logger.debug("%s:%s" % (key, val))
            # 要Bind的主机信息
            host_obj = session.query(models.Host).filter(models.Host.hostname == val.get('hostname')).first()
            logger.debug("host_obj---\n%s" % host_obj)
            assert host_obj
            for item in val['remote_users']:  # 要bind到该主机上的账户信息
                logger.debug(item)
                assert item.get('auth_type')
                if item.get('auth_type') == 'ssh-password':
                    remoteuser_obj = session.query(models.RemoteUser).filter(
                        models.RemoteUser.username == item.get('username'),
                        models.RemoteUser.password == item.get('password')
                    ).first()
                else:
                    remoteuser_obj = session.query(models.RemoteUser).filter(
                        models.RemoteUser.username == item.get('username'),
                        models.RemoteUser.auth_type == item.get('auth_type'),
                    ).first()
                if not remoteuser_obj:
                    print_err("RemoteUser obj %s does not exist." % item, logout=True)
                bindhost_obj = models.BindHost(host_id=host_obj.id, remoteuser_id=remoteuser_obj.id)  # 设定bind关系
                session.add(bindhost_obj)
                # for groups this host binds to 该主机bind到主机组
                if source[key].get('groups'):
                    group_objs = session.query(models.HostGroup).filter(
                        models.HostGroup.name.in_(source[key].get('groups'))).all()
                    assert group_objs
                    logger.info('groups:%s' % group_objs)
                    bindhost_obj.host_groups = group_objs
                # for user_profiles this host binds to  该主机bind到的用户
                if source[key].get('user_profiles'):
                    userprofile_objs = session.query(models.UserProfile).filter(models.UserProfile.username.in_(
                        source[key].get('user_profiles')
                    )).all()
                    logger.debug(userprofile_objs)
                    assert userprofile_objs
                    logger.info("userprofiles:%s" % userprofile_objs)
                    bindhost_obj.user_profiles = userprofile_objs
                    # print(bindhost_obj)
        session.commit()
        logger.info("create bindhosts sucess!")


def start_session(argvs):
    print('going to start sesssion ')
    user = auth()  # 用户登录堡垒机
    if user:
        welcome_msg(user)
        # print(user.bind_hosts)  # 用户管理的主机
        # print(user.host_groups)  # 用户管理的主机组
        exit_flag = False
        while not exit_flag:
            if user.bind_hosts:
                print('\033[32;1mz.\tungroupped hosts (%s)\033[0m' % len(user.bind_hosts))  # 主机数
            for index, group in enumerate(user.host_groups):
                print('\033[32;1m%s.\t%s (%s)\033[0m' % (index, group.name, len(group.bind_hosts)))  # 主机组及主机数量

            choice = input("[%s]:" % user.username).strip()
            if len(choice) == 0:
                continue
            if choice == 'z':  # 非分组主机信息
                print("------ Group: ungroupped hosts ------")
                for index, bind_host in enumerate(user.bind_hosts):
                    print("  %s.\t%s@%s(%s)" % (index,
                                                bind_host.remote_user.username,
                                                bind_host.host.hostname,
                                                bind_host.host.ip,
                                                ))
                print("----------- END -----------")

                # host selection
                while not exit_flag:
                    user_option = input("[(b)back, (q)quit, select host to login]:").strip()  # 选择主机进行操作
                    if len(user_option) == 0:
                        continue
                    if user_option == 'b':
                        break
                    if user_option == 'q':
                        exit_flag = True
                    if user_option.isdigit():
                        user_option = int(user_option)
                        if user_option < len(user.bind_hosts):
                            print('host:', user.bind_hosts[user_option])
                            print('audit log:', user.bind_hosts[user_option].audit_logs)
                            ssh_login.ssh_login(user,  # 堡垒机用户信息
                                                user.bind_hosts[user_option],
                                                session,
                                                log_recording)

            elif choice.isdigit():
                choice = int(choice)
                if choice < len(user.host_groups):  # 分组的主机信息
                    print("------ Group: %s ------" % user.host_groups[choice].name)
                    for index, bind_host in enumerate(user.host_groups[choice].bind_hosts):
                        print("  %s.\t%s@%s(%s)" % (index,
                                                    bind_host.remote_user.username,
                                                    bind_host.host.hostname,
                                                    bind_host.host.ip,
                                                    ))
                    print("----------- END -----------")

                    # host selection
                    while not exit_flag:
                        user_option = input("[(b)back, (q)quit, select host to login]:").strip()  # 选择主机进行操作
                        if len(user_option) == 0:
                            continue
                        if user_option == 'b':
                            break
                        if user_option == 'q':
                            exit_flag = True
                        if user_option.isdigit():
                            user_option = int(user_option)
                            if user_option < len(user.host_groups[choice].bind_hosts):
                                print('host:', user.host_groups[choice].bind_hosts[user_option])
                                print('audit log:', user.host_groups[choice].bind_hosts[user_option].audit_logs)
                                ssh_login.ssh_login(user,  # 堡垒机用户信息
                                                    user.host_groups[choice].bind_hosts[user_option],
                                                    session,
                                                    log_recording)
        else:
            print("no this option..")


def auth():
    """
    do the user login authentication
    :return:
    """
    count = 0
    while count < 3:
        username = input("\033[32;1mUsername:\033[0m").strip()
        if len(username) == 0:
            continue
        password = input("\033[32;1mPassword:\033[0m").strip()
        if len(password) == 0:
            continue
        user_obj = session.query(models.UserProfile).filter(models.UserProfile.username == username,
                                                            models.UserProfile.password == password).first()
        if user_obj:
            return user_obj
        else:
            print("wrong username or password, you have %s more chances." % (3 - count - 1))
            count += 1
    else:
        print_err("too many attempts.")


def log_recording(user_obj, bind_host_obj, logs):
    """
    flush user operations on remote host into DB
    :param user_obj:
    :param bind_host_obj:
    :param logs: list format [logItem1,logItem2,...]
    :return:
    """

    print("\033[41;1m--logs:\033[0m", logs)
    session.add_all(logs)
    session.commit()


def welcome_msg(user):
    msg = '''\033[32;1m
    ------------- Welcome [%s] login BastionHost -------------
    \033[0m''' % user.username
    print(msg)
