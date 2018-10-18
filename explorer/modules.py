# -*- coding: utf-8 -*-

# Display information for TiDB modules

import json
import logging

from datetime import datetime

from explorer import tui
from utils import fileopt
from utils import util


class TUIModuleBase(tui.TUIBase):
    def __init__(self, args, module=None):
        super(TUIModuleBase, self).__init__(args)

        if not module:
            self.hosts = self.inventory.get_hosts(
                '%s_servers' % args.subcmd_show)
        else:
            self.hosts = self.inventory.get_hosts('%s_servers' % module)


class TUIModule(TUIModuleBase):
    def __init__(self, args):
        super(TUIModule, self).__init__(args)

        if args.subcmd_show == 'tidb':
            self.module = TUIModuleTiDB(args)
        elif args.subcmd_show == 'tikv':
            self.module = TUIModuleTiKV(args)
        elif args.subcmd_show == 'pd':
            self.module = TUIModulePD(args)

    def display(self):
        self.module.display()


class TUIModuleTiDB(TUIModuleBase):
    def __init__(self, args):
        super(TUIModuleTiDB, self).__init__(args, module='tidb')
        self.tidbinfo = {}

        for host in self.hosts:
            host = str(host)
            self.tidbinfo[host] = {}
            # list all tidbinfo information of this host
            for file in fileopt.list_files(self.datadir, filter='%s/tidbinfo/' % host):
                key = file.split('-tidb-')[-1][:-5]
                self.tidbinfo[host][key] = json.loads(fileopt.read_file(file))

    def build_tidb_info(self):
        result = []

        info = []
        info.append([''])
        status = []
        status.append([''])
        info.append(['Host', 'AdvAddr', 'Store', 'Version'])
        status.append(['Host', 'DDL-ID', 'Conn', 'Region',
                       'MemRSS', 'VMS', 'Swap', 'Owner', 'Running'])
        for host, stats in self.tidbinfo.items():
            host_alias = 'tidb_%s' % host
            _setting = stats['settings']
            _info = stats['info']
            _stat = stats['status']
            _proc = None
            for proc in self.collector[host_alias]['proc_stats']:
                if 'tidb' in proc['name']:
                    _proc = proc['memory']
                    start_time = util.format_time_seconds(
                        self.collector[host_alias]['meta']['uptime'] - proc['start_time'])
                else:
                    continue

                info.append([
                    host,
                    '%s:%s' % (_setting['advertise-address'],
                               _info['listening_port']),
                    '%s %s' % (_setting['store'], _setting['path']),
                    '%s %s' % (_info['version'],
                               '*' if _info['is_owner'] else '')
                ])
                status.append([
                    host,
                    _info['ddl_id'],
                    '%s' % _stat['connections'],
                    '%s' % len(stats['regions']),
                    util.format_size_bytes(_proc['rss']) if _proc else '',
                    util.format_size_bytes(_proc['vms']) if _proc else '',
                    util.format_size_bytes(_proc['swap']) if _proc else '',
                    '*' if _info['is_owner'] else '',
                    start_time
                ])
        result.append(info)
        result.append(status)

        return result

    def display(self):
        for section in self.build_tidb_info():
            for row in self.format_columns(section):
                print(row)


class TUIModuleTiKV(TUIModuleBase):
    def __init__(self, args):
        super(TUIModuleTiKV, self).__init__(args, 'tikv')

    def build_tikv_info(self):
        result = []

        info = []
        info.append([''])
        info.append(['Host', 'AdvAddr', 'Version', 'PD',
                     'MemRSS', 'VMS', 'Swap', 'Running'])
        for host in self.hosts:
            host = str(host)
            host_alias = 'tikv_%s' % host
            _proc = None
            for proc in self.collector[host_alias]['proc_stats']:
                if 'tikv' in proc['name']:
                    _proc = proc
                    start_time = util.format_time_seconds(
                        self.collector[host_alias]['meta']['uptime'] - proc['start_time'])
                else:
                    continue
                if not _proc:
                    continue

                _cmd = _proc['cmd'].split()
                try:
                    adv_addr = _cmd[_cmd.index('--advertise-addr') + 1]
                except ValueError:
                    adv_addr = ''
                try:
                    pd_addr = _cmd[_cmd.index('--pd') + 1]
                except ValueError:
                    pd_addr = ''
                try:
                    for tikv_vers in self.collector[host_alias]['meta']['tikv']:
                        if tikv_vers['pid'] != _proc['pid']:
                            continue
                        rel_ver = '%s-g%s' % (tikv_vers['release_version'],
                                              tikv_vers['git_commit'][:6])
                except KeyError:
                    rel_ver = ''
                info.append([
                    host, adv_addr, rel_ver, pd_addr,
                    util.format_size_bytes(
                        _proc['memory']['rss']) if _proc else '',
                    util.format_size_bytes(
                        _proc['memory']['vms']) if _proc else '',
                    util.format_size_bytes(
                        _proc['memory']['swap']) if _proc else '',
                    start_time
                ])
        result.append(info)

        return result

    def display(self):
        for section in self.build_tikv_info():
            for row in self.format_columns(section):
                print(row)


class TUIModulePD(TUIModuleBase):
    def __init__(self, args):
        super(TUIModulePD, self).__init__(args, 'pd')
        self.pdinfo = {}

        for host in self.hosts:
            host = str(host)
            self.pdinfo[host] = {}
            # list all pdctl information of this host
            for file in fileopt.list_files(self.datadir, filter='%s/pdctl/' % host):
                key = file.split('-')[-1][:-5]
                self.pdinfo[host][key] = json.loads(fileopt.read_file(file))

    def build_pd_cluster_info(self):
        result = {}
        for host in self.hosts:
            host = str(host)
            try:
                id = self.pdinfo[host]['members']['header']['cluster_id']
                result[id] = {}
            except KeyError:
                continue
            for member in self.pdinfo[host]['members']['members']:
                member_id = member['member_id']
                tmp = {
                    'name': member['name'],
                    'peer': member['peer_urls'],
                    'leader': True if member_id == self.pdinfo[host]['members']['leader']['member_id'] else False,
                    'etcd_leader': True if member_id == self.pdinfo[host]['members']['etcd_leader']['member_id'] else False,
                }
                try:
                    result[id][member_id].append(tmp)
                except KeyError:
                    result[id][member_id] = [tmp]
            # All PD members reports the same members.json stats
            break
        return result

    def build_pd_info(self):
        result = []
        cluster_stats = self.build_pd_cluster_info()

        header = []
        header.append(['\n* PD Servers:'])
        header.append(['Host', 'Name', 'Version', 'URL',
                       'MemRSS', 'VMS', 'Swap', 'Running'])
        for host in self.hosts:
            host = str(host)
            host_alias = 'pd_%s' % host
            _proc = None
            for proc in self.collector[host_alias]['proc_stats']:
                if 'pd' in proc['name']:
                    _proc = proc
                    start_time = util.format_time_seconds(
                        self.collector[host_alias]['meta']['uptime'] - proc['start_time'])
                else:
                    continue
                if not _proc:
                    continue
                _info = self.pdinfo[host]

                header.append([
                    host, _info['config']['name'], _info['config']['cluster-version'],
                    _info['config']['advertise-peer-urls'],
                    util.format_size_bytes(
                        _proc['memory']['rss']) if _proc else '',
                    util.format_size_bytes(
                        _proc['memory']['vms']) if _proc else '',
                    util.format_size_bytes(
                        _proc['memory']['swap']) if _proc else '',
                    start_time
                ])
        result.append(header)

        cluster_info = []
        cluster_info.append(["\n* Cluster:"])
        for cluster_id, cluster in cluster_stats.items():
            cluster_info.append(['ID: %s' % cluster_id])
            cluster_info.append(['ID', 'Node', 'L', 'EL', 'Peer', 'Health'])
            for member_id, nodes in cluster.items():
                for node in nodes:
                    cluster_info.append([
                        '%s' % member_id,
                        node['name'],
                        '*' if node['leader'] else ' ',
                        '*' if node['etcd_leader'] else ' ',
                        ','.join(node['peer']),
                        [str(_pd['health']) for _pd in self.pdinfo[host]
                         ['health'] if _pd['member_id'] == member_id][0]
                    ])
        result.append(cluster_info)

        return result

    def display(self):
        for section in self.build_pd_info():
            for row in self.format_columns(section):
                print(row)
