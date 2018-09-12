# -*- coding: utf-8 -*-

# List servers in cluster

import logging

from explorer import tui
from utils import util


class TUIServers(tui.TUIBase):
    def __init__(self, args):
        # init file list and inventory
        super(TUIServers, self).__init__(args)

        # map roles to hosts
        self.host_roles = {}
        for group, hosts in self.inventory.get_groups_dict().items():
            if group == 'all':
                continue
            role = group[:-8] if group.endswith('_servers') else group
            # monitored_servers are all hosting servers, other roles may be
            # instances on hosting servers
            if group == 'monitored_servers':
                role = 'host'
            for host in hosts:
                try:
                    self.host_roles[host].add(role)
                except KeyError:
                    self.host_roles[host] = set()
                    self.host_roles[host].add(role)

    def display(self):
        output = [['Server', 'Roles']]
        for host, roles in self.host_roles.items():
            row = [host]
            role_list = list(roles)
            role_list.sort()
            row.append(','.join(role_list))
            output.append(row)
        for row in self.format_columns(output):
            print(row)
