#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhangrf
# E-mail: 78769488@qq.com
# Create: 2017/3/30

from sqlalchemy import Table, Column, Integer, String, DATETIME, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import ChoiceType

from sqlalchemy import create_engine

# from sqlalchemy.orm import sessionmaker


Base = declarative_base()

user_m2m_bindhost = Table('user_m2m_bindhost', Base.metadata,
                          Column('userprofile_id', Integer, ForeignKey('user_profile.id')),
                          Column('bindhost_id', Integer, ForeignKey('bind_host.id')),
                          )
bindhost_m2m_hostgroup = Table('bindhost_m2m_hostgroup', Base.metadata,
                               Column('bindhost_id', Integer, ForeignKey('bind_host.id')),
                               Column('hostgroup_id', Integer, ForeignKey('host_group.id')),
                               )

user_m2m_hostgroup = Table('userprofile_m2m_hostgroup', Base.metadata,
                           Column('userprofile_id', Integer, ForeignKey('user_profile.id')),
                           Column('hostgroup_id', Integer, ForeignKey('host_group.id')),
                           )


class Host(Base):
    __tablename__ = 'host'
    id = Column(Integer, primary_key=True)
    hostname = Column(String(64), unique=True)
    ip = Column(String(64), unique=True)
    port = Column(Integer, default=22)

    def __repr__(self):
        return self.hostname


class HostGroup(Base):
    __tablename__ = 'host_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    bind_hosts = relationship("BindHost", secondary="bindhost_m2m_hostgroup", backref="host_groups")

    def __repr__(self):
        return self.name


class RemoteUser(Base):
    __tablename__ = 'remote_user'
    __table_args__ = (UniqueConstraint('auth_type', 'username', 'password', name='_user_passwd_uc'),)

    id = Column(Integer, primary_key=True)
    AuthTypes = [
        ('ssh-password', 'SSH/Password'),
        ('ssh-key', 'SSH/KEY'),
    ]
    auth_type = Column(ChoiceType(AuthTypes))
    username = Column(String(32))
    password = Column(String(128))

    def __repr__(self):
        return self.username


class BindHost(Base):
    """
    主机与主机用户名关联关系
    192.168.1.11    web
    192.168.1.11    mysql
    """
    __tablename__ = "bind_host"
    __table_args__ = (UniqueConstraint('host_id', 'remoteuser_id', name='_host_remoteuser_uc'),)

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('host.id'))
    remoteuser_id = Column(Integer, ForeignKey('remote_user.id'))
    host = relationship("Host", backref="bind_hosts")
    remote_user = relationship("RemoteUser", backref="bind_hosts")

    def __repr__(self):
        return "<%s -- %s >" % (self.host.ip, self.remote_user.username)


class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    password = Column(String(128))
    bind_hosts = relationship("BindHost", secondary='user_m2m_bindhost', backref="user_profiles")
    host_groups = relationship("HostGroup", secondary="userprofile_m2m_hostgroup", backref="user_profiles")

    def __repr__(self):
        return self.username


class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profile.id'))
    bind_host_id = Column(Integer, ForeignKey('bind_host.id'))

    action_choices = [
        ('cmd', 'CMD'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        # ("getfile", 'GetFile'),
        # ("sendfile", 'SendFile'),
        # ("exception", 'Exception'),
    ]
    action_type = Column(ChoiceType(action_choices))
    cmd = Column(String(255))
    date = Column(DATETIME)

    user_profile = relationship("UserProfile")  # 不需要反查关系
    bind_host = relationship("BindHost")

    def __repr__(self):
        return "<user=%s,host=%s,action=%s,cmd=%s,date=%s>" % (self.user_profile.username,
                                                               self.bind_host.host.hostname,
                                                               self.action_type,
                                                               self.cmd,
                                                               self.date)


if __name__ == "__main__":
    engine = create_engine("mysql+pymysql://root:alex3714@192.168.16.86/oldboydb?charset=utf8",
                           )
    Base.metadata.create_all(engine)  # 创建表结构
