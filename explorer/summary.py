# -*- coding: utf-8 -*-

# Display summary information of TiDB cluster

import json
import logging

from collections import Counter
from datetime import datetime

from explorer import modules
from explorer import tui
from utils import fileopt
from utils import util


class TUISummary(tui.TUIBase):
    def __init__(self, args):
        super(TUISummary, self).__init__(args)
        self.tidb = modules.TUIModuleTiDB(args)
        self.tikv = modules.TUIModuleTiKV(args)
        self.pd = modules.TUIModulePD(args)

    def item_count(self, iterable_obj):
        result = []
        cnt = Counter(iterable_obj)
        for item in set(iterable_obj):
            result.append('%s(%s)' % (item, cnt[item]))
        return ','.join(result)

    def build_summary_info(self):
        result = []

        tidb = []
        tidb.append(['\nTiDB Servers:'])
        result.append(tidb)
        result += self.tidb.build_tidb_info()

        tikv = []
        tikv.append(['\nTiKV Servers:'])
        result.append(tikv)
        result += self.tikv.build_tikv_info()

        pd = []
        pd.append(['\nPD Servers:'])
        result.append(pd)
        result += self.pd.build_pd_info()

        summary = []
        summary.append(['\nSummary:'])
        summary.append(['Module', 'Num', 'Versions'])
        sum_tidb = ['TiDB', '%s' % len(self.tidb.hosts),
                    self.item_count([item['info']['version']
                                     for item in self.tidb.tidbinfo.values()])
                    ]
        summary.append(sum_tidb)

        tikv_versions = []
        for tikv_host in self.tikv.hosts:
            tikv_host = str(tikv_host)
            try:
                rel_ver = '%s-g%s' % (self.tikv.collector[tikv_host]['meta']['tikv']['release_version'],
                                      self.tikv.collector[tikv_host]['meta']['tikv']['git_commit'][:6])
                tikv_versions.append(rel_ver)
            except KeyError:
                continue
        sum_tikv = ['TiKV', '%s' % len(self.tikv.hosts),
                    self.item_count(tikv_versions)
                    ]
        summary.append(sum_tikv)

        sum_pd = ['PD', '%s' % len(self.pd.hosts),
                  self.item_count([item['config']['cluster-version']
                                   for item in self.pd.pdinfo.values()])
                  ]
        summary.append(sum_pd)

        result.append(summary)

        return result

    def display(self):
        for section in self.build_summary_info():
            for row in self.format_columns(section):
                print(row)
