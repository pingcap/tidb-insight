# -*- coding: utf-8 -*-

# List servers in cluster

import logging

from datetime import datetime

from explorer import tui
from utils import util


class TUIServerList(tui.TUIBase):
    def __init__(self, args):
        # init file list and inventory
        super(TUIServerList, self).__init__(args)

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
        return output

    def display(self):
        for row in self.format_columns(self.build_server_list()):
            print(row)


class TUIServerInfo(TUIServerList):
    def __init__(self, args):
        super(TUIServerInfo, self).__init__(args)

        self.host = args.hostalias

    def build_server_info(self):
        result = []
        _sys = self.collector[self.host]

        result.append([['\n* System:']])
        header = []
        # strip milisec part of the time string to 6 digits
        _time = _sys['meta']['timestamp'][:-9] + _sys['meta']['timestamp'][-6:]
        collect_time = datetime.strptime(_time, '%Y-%m-%dT%H:%M:%S.%f%z')
        try:
            uptime = util.format_time_seconds(_sys['meta']['uptime'])
        except KeyError:
            uptime = 'N/A'
        header.append([
            'Time:', '%s' % collect_time.strftime('%Y-%m-%d %T %Z'),
            'NTP Status:', '%s %s (offest: %sms)' % (_sys['ntp']['status'],
                                                     _sys['ntp']['sync'],
                                                     _sys['ntp']['offset']),
            'UP:', uptime
        ])
        header.append([
            'BIOS:', '%s %s %s' % (_sys['sysinfo']['bios']['vendor'],
                                   _sys['sysinfo']['bios']['version'],
                                   _sys['sysinfo']['bios']['date']),
            'Kernel:', '%s %s' % (_sys['sysinfo']['kernel']['release'],
                                  _sys['sysinfo']['kernel']['architecture'])
        ])
        result.append(header)

        sysinfo = []
        try:
            os_release = '%s %s %s' % (
                _sys['sysinfo']['os']['name'], _sys['sysinfo']['os']['release'], _sys['sysinfo']['os']['architecture'])
        except KeyError:
            os_release = '%s %s' % (
                _sys['sysinfo']['os']['name'], _sys['sysinfo']['os']['architecture'])
        sysinfo.append([
            'Host:', '%s' % _sys['sysinfo']['node']['hostname'],
            'Alias:', '%s' % self.host,
            'OS:', os_release
        ])
        server_type = '%s %s' % (
            _sys['sysinfo']['product']['vendor'], _sys['sysinfo']['product']['name'])
        try:
            server_type += ' %s' % _sys['sysinfo']['product']['serial']
        except KeyError:
            pass
        sysinfo.append([
            'CPU:', '%s %.2fGHz x%s' % (_sys['sysinfo']['cpu']['vendor'],
                                        _sys['sysinfo']['cpu']['speed'] / 1000.0,
                                        _sys['sysinfo']['cpu']['threads']),
            'Mem:', '%.1fGB %s' % (_sys['sysinfo']['memory']['size'] / 1024.0,
                                   _sys['sysinfo']['memory']['type']),
            'Type:', server_type
        ])
        result.append(sysinfo)

        network = []
        result.append([['\n* Network:']])
        for interface in _sys['sysinfo']['network']:
            network.append([
                'Interface: %s (%s)' % (
                    interface['name'], interface['driver']),
                'MAC: %s' % interface['macaddress']
            ])
            network.append(['IP(s): %s' % ', '.join(interface['ipaddress'])])
        result.append(network)

        storage = []
        result.append([['\n* Storage:']])
        storage.append(['Name', 'Size', 'FS', 'MountPoint', 'MountOptions'])
        storage += self.parse_partitions(_sys['partitions'])
        result.append(storage)

        return result

    def parse_partitions(self, devlist, prefix=None):
        result = []
        for dev in devlist:
            name = dev['name'] if not prefix else '%s─%s' % (
                prefix, dev['name'])
            size = util.format_size_bytes(dev['size'])
            try:
                mp = dev['mount']['mount_point']
            except KeyError:
                mp = ''
            try:
                mo = dev['mount']['mount_options']
            except KeyError:
                mo = ''
            try:
                fs = dev['mount']['filesystem']
            except KeyError:
                fs = ''

            result.append([name, size, fs, mp, mo])

            if 'subdev' in dev.keys():
                subprefix = prefix if prefix else '├'
                sub_result = self.parse_partitions(
                    dev['subdev'], '  ' + subprefix)
                result[-1][0] = result[-1][0].replace('├', '└')
                sub_result[-1][0] = sub_result[-1][0].replace('├', '└')
                result += sub_result

        return result

    def display(self):
        for section in self.build_server_info():
            for row in self.format_columns(section):
                print(row)
