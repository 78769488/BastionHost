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
from modules.db_conn import engine

# from sqlalchemy.orm import sessionmaker


Base = declarative_base()

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

    user_profile = relationship("UserProfile", backref="audit_logs")
    bind_host = relationship("BindHost", backref="audit_logs")

    def __repr__(self):
        return "<user=%s,host=%s,action=%s,cmd=%s,date=%s>" % (self.user_profile.username,
                                                               self.bind_host.host.hostname,
                                                               self.action_type,
                                                               self.cmd,
                                                               self.date)


if __name__ == "__main__":
    # engine = create_engine("mysql+pymysql://root:alex3714@192.168.16.86/oldboydb?charset=utf8",
    #                        )
    Base.metadata.create_all(engine)  # 创建表结构
