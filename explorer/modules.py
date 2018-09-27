# -*- coding: utf-8 -*-

# Display information for TiDB modules

import logging

from datetime import datetime

from explorer import tui
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

    def build_module_info(self):
        # TODO: one host per line: pid, data_dir(dev), log_dir(dev), proc_mem, proc_cpu
        #      info from PD & tidb apis
        for host in self.hosts:
            print(host)

    def display(self):
        self.build_module_info()
