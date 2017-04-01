#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhangrf
# E-mail: 78769488@qq.com
# Create: 2017/3/30


from modules import views

actions = {
    'syncdb': views.syncdb,
    'audit_user': views.audit_recording,
    'start_session': views.start_session,
    # 'stop': views.stop_server,
    'create_hosts': views.create_hosts,
    'create_remoteusers': views.create_remoteusers,
    'create_users': views.create_users,
    'create_groups': views.create_groups,
    'create_bindhosts': views.create_bindhosts,

}
