# -*- coding: utf-8 -*-

# Base Class for all measurement features

import os

from abc import ABCMeta
from abc import abstractmethod

from utils import fileopt


class MeasurementBase(object):
    __metaclass__ = ABCMeta

    def __init__(self, args, basedir=None, subdir=None):
        self.options = args
        self.outdir = fileopt.build_full_output_dir(
            basedir=basedir, subdir=subdir)

    @abstractmethod
    def run_collecting(self):
        pass
