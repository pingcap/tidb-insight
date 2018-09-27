# -*- coding: utf-8 -*-

# Display information for TiDB modules

import json
import logging

from datetime import datetime

from explorer import tui
from utils import fileopt
from utils import util


class TUIModuleBase(tui.TUIBase):
    def __init__(self, args):
        super(TUIModuleBase, self).__init__(args)

        self.hosts = self.inventory.get_hosts('%s_servers' % args.subcmd_show)


class TUIModule(TUIModuleBase):
    def __init__(self, args):
        super(TUIModule, self).__init__(args)

        if args.subcmd_show == 'tidb':
            self.module = TUIModuleTiDB(args)
        elif args.subcmd_show == 'tikv':
            self.module = TUIModuleTiKV(args)

    def display(self):
        self.module.display()


class TUIModuleTiDB(TUIModuleBase):
    def __init__(self, args):
        super(TUIModuleTiDB, self).__init__(args)
        self.tidbinfo = {}

        for host in self.hosts:
            host = str(host)
            self.tidbinfo[host] = {}
            # list all tidbinfo information of this host
            for file in fileopt.list_files(self.datadir, filter='%s/tidbinfo' % host):
                key = file.split('-tidb-')[-1][:-5]
                self.tidbinfo[host][key] = json.loads(fileopt.read_file(file))

    def build_tidb_info(self):
        result = []

        info = []
        status = []
        info.append(['Host', 'AdvAddr', 'Store', 'Version'])
        status.append(['Host', 'DDL-ID', 'Conns', 'Regions',
                       'MemRSS', 'VMS', 'Swap', 'Owner'])
        for host, stats in self.tidbinfo.items():
            _setting = stats['settings']
            _info = stats['info']
            _stat = stats['status']
            _proc = None
            for proc in self.collector[host]['proc_stats']:
                if 'tidb' in proc['name']:
                    _proc = proc['memory']

            info.append([
                host,
                '%s:%s' % (_setting['advertise-address'],
                           _info['listening_port']),
                '%s %s' % (_setting['store'], _setting['path']),
                '%s %s' % (_info['version'], '*' if _info['is_owner'] else '')
            ])
            status.append([
                host,
                _info['ddl_id'],
                '%s' % _stat['connections'],
                '%s' % len(stats['regions']),
                util.format_size_bytes(_proc['rss']) if _proc else '',
                util.format_size_bytes(_proc['vms']) if _proc else '',
                util.format_size_bytes(_proc['swap']) if _proc else '',
                '*' if _info['is_owner'] else ''
            ])
        result.append(info)
        result.append(status)

        return result

    def display(self):
        for section in self.build_tidb_info():
            print('')
            for row in self.format_columns(section):
                print(row)


class TUIModuleTiKV(TUIModuleBase):
    def __init__(self, args):
        super(TUIModuleTiKV, self).__init__(args)
        self.tikvinfo = {}

    def build_tikv_info(self):
        result = []

        info = []
        info.append(['Host', 'AdvAddr', 'Version',
                     'PD', 'MemRSS', 'VMS', 'Swap'])
        for host in self.hosts:
            host = str(host)
            _proc = None
            for proc in self.collector[host]['proc_stats']:
                if 'tikv' in proc['name']:
                    _proc = proc
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
                rel_ver = '%s-g%s' % (self.collector[host]['meta']['tikv']['release_version'],
                                      self.collector[host]['meta']['tikv']['git_commit'][:6])
            except KeyError:
                rel_ver = ''
            info.append([
                host, adv_addr, rel_ver, pd_addr,
                util.format_size_bytes(
                    _proc['memory']['rss']) if _proc else '',
                util.format_size_bytes(
                    _proc['memory']['vms']) if _proc else '',
                util.format_size_bytes(
                    _proc['memory']['swap']) if _proc else ''
            ])
        result.append(info)

        return result

    def display(self):
        for section in self.build_tikv_info():
            print('')
            for row in self.format_columns(section):
                print(row)
