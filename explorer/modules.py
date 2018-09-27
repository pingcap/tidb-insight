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

    def build_module_info(self):
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
        for section in self.build_module_info():
            print('')
            for row in self.format_columns(section):
                print(row)
