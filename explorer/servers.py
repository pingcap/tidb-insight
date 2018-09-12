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
            if group == 'monitored_servers':
                role = 'exporter'
            elif group == 'monitoring_servers':
                role = 'monitor'
            elif group == 'alertmanager_servers':
                role = 'alert'
            for host in hosts:
                try:
                    self.host_roles[host].add(role)
                except KeyError:
                    self.host_roles[host] = set()
                    self.host_roles[host].add(role)

    def build_server_list(self):
        output = []
        column_headers = ['Server', 'VM', 'OS', 'Kernel', 'Roles']
        for host, roles in self.host_roles.items():
            row = [host]

            # basic system info
            sysinfo = self.collector[host]['sysinfo']
            # check if virtual machines
            try:
                row.append(sysinfo['node']['hypervisor'])
            except KeyError:
                row.append('No')
            # system version
            row.append(sysinfo['os']['name'])
            row.append(sysinfo['kernel']['release'])

            role_list = list(roles)
            role_list.sort()
            row.append(','.join(role_list))

            output.append(row)

        output.sort()
        output = [column_headers] + output
        for row in self.format_columns(output):
            print(row)

    def display(self):
        self.build_server_list()
