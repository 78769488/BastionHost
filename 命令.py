dic = {
    'bind2': {
        'groups': ['bj_group', 'sh_group'],
        'user_profiles': ['rain'],
        'hostname': 'server2',
        'remote_users': [{'username': 'root', 'password': 'abc!23', 'auth_type': 'ssh-password', 'user1': None}]
    },

    'bind1': {
        'groups': ['bj_group'],
        'user_profiles': ['alex', 'jack'],
        'hostname': 'ubuntu test',
        'remote_users': [
            {'username': 'root', 'auth_type': 'ssh-key', 'user1': None},
            {'user2': None, 'username': 'alex', 'password': 'alex3714', 'auth_type': 'ssh-password'}
        ]
    }
}

#
# syncdb
#
# create_hosts  -f E:\PycharmProjects\day13\BastionHost\data\examples\new_hosts.yml
# create_remoteusers -f E:\PycharmProjects\day13\BastionHost\data\examples\new_remoteusers.yml
# create_users -f E:\PycharmProjects\day13\BastionHost\data\examples\new_user.yml
# create_bindhosts -f E:\PycharmProjects\day13\BastionHost\data\examples\new_bindhosts.yml
# create_groups  -f E:\PycharmProjects\day13\BastionHost\data\examples\new_groups.yaml
#


# actions = {
#     'start_session': views.start_session,
#     # 'stop': views.stop_server,
#     'syncdb': views.syncdb,
#     'create_hosts': views.create_hosts,
#     'create_remoteusers': views.create_remoteusers,
#     'create_users': views.create_users,
#     'create_groups': views.create_groups,
#     # 'create_bindhosts': views.create_bindhosts,
#     # 'create_remoteusers': views.create_remoteusers,
#     # 'audit':views.log_audit
#
# }
