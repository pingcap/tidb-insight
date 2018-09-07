# -*- coding: utf-8 -*-

# Base Class for basic TUI features

import logging

from abc import abstractmethod

from utils import fileopt
from utils import util


class TUIBase():
    def __init__(self, args):
        self.datadir = args.dir
        if not self.datadir:
            raise ValueError("Data dir must be set.")
        logging.debug("Using data dir: %s" % self.datadir)
        self.file_list = fileopt.list_files(self.datadir)

    # adjust column width to fit the longest content
    def format_columns(self, data):
        result = []
        col_width = max(len(word) for row in data for word in row) + 2
        for row in data:
            result.append("".join(word.ljust(col_width) for word in row))
        return result

    @abstractmethod
    def display(self):
        raise NotImplementedError
