# -*- coding: utf-8 -*-

# Base Class for basic TUI features

import json
import logging

from abc import abstractmethod
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

from utils import fileopt
from utils import util


class TUIBase(object):
    def __init__(self, args):
        self.datadir = args.input
        if not self.datadir:
            raise ValueError("Data dir must be set with `-i/--input`.")
        logging.debug("Using data dir: %s" % self.datadir)
        self.file_list = fileopt.list_files(self.datadir)
        logging.debug("Found %s files in data directory." %
                      len(self.file_list))
        self.inventory = self.read_ansible_inventory()
        self.collector = self.read_collector_data()

    # adjust column width to fit the longest content
    def format_columns(self, data):
        result = []
        col_width = []
        for row in data:
            i = 0
            for word in row:
                try:
                    col_width[i] = max(len(word), col_width[i])
                except IndexError:
                    col_width.append(len(word))
                i += 1
        for row in data:
            i = 0
            wide_row = []
            for word in row:
                wide_row.append(word.ljust(col_width[i] + 2))
                i += 1
            result.append("".join(wide_row))
        return result

    def read_ansible_inventory(self):
        try:
            inventory_file = [
                file for file in self.file_list if file.endswith('inventory.ini')][0]
        except IndexError:
            logging.warning(
                "No inventory.ini found, results may be incomplete.")
            return None
        logging.debug("Found and reading Ansible inventory file: %s" %
                      inventory_file)
        loader = DataLoader()
        return InventoryManager(loader=loader, sources=inventory_file)

    def read_collector_data(self):
        data = {}
        for file in self.file_list:
            # paths are like some/path/<host_alias>/collector/<key>.json
            if 'collector/' not in file or not file.endswith('.json'):
                continue
            _path = file.split('/')
            alias = _path[-3]
            key = _path[-1][:-5]  # remove the '.json' suffix
            _data = json.loads(fileopt.read_file(file))
            try:
                data[alias][key] = _data
            except KeyError:
                data[alias] = {key: _data}
        return data

    @abstractmethod
    def display(self):
        raise NotImplementedError
