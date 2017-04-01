#!/usr/bin/env python
# -*- coding=utf-8 -*-
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conf import settings

engine = create_engine(settings.DB_CONN, echo=False)

SessionCls = sessionmaker(bind=engine)  # 创建与数据库的会话session class ,注意,这里返回给session的是个class,不是实例
session = SessionCls()


# pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
#
# redis_log = redis.Redis(connection_pool=pool)
redis_log = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
