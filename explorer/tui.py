# -*- coding: utf-8 -*-

# Base Class for basic TUI features

import logging

from abc import abstractmethod
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

from utils import fileopt
from utils import util


class TUIBase(object):
    def __init__(self, args):
        self.datadir = args.dir
        if not self.datadir:
            raise ValueError("Data dir must be set.")
        logging.debug("Using data dir: %s" % self.datadir)
        self.file_list = fileopt.list_files(self.datadir)
        logging.debug("Found %s files in data directory." %
                      len(self.file_list))
        self.inventory = self.read_ansible_inventory()

    # adjust column width to fit the longest content
    def format_columns(self, data):
        result = []
        col_width = max(len(word) for row in data for word in row) + 2
        for row in data:
            result.append("".join(word.ljust(col_width) for word in row))
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

    @abstractmethod
    def display(self):
        raise NotImplementedError
