# -*- coding: utf-8 -*-

# List servers in cluster

import logging

from explorer import tui
from utils import util


class TUIServers(tui.TUIBase):
    def __init__(self, args):
        # init file list
        super(TUIServers, self).__init__(args)

    # adjust column width to fit the longest content
    def format_columns(self, data):
        result = []
        col_width = max(len(word) for row in data for word in row) + 2
        for row in data:
            result.append("".join(word.ljust(col_width) for word in row))
        return result

    def display(self):
        print("Dummy output.")
