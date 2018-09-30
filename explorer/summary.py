# -*- coding: utf-8 -*-

# Display summary information of TiDB cluster

import json
import logging

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

        return result

    def display(self):
        for section in self.build_summary_info():
            for row in self.format_columns(section):
                print(row)
