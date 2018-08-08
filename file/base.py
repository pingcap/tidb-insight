# -*- coding: utf-8 -*-

# Base Class for all file collecting features

import datetime
import logging
import os
import shutil
import time

from abc import abstractmethod

from utils import fileopt
from utils.measurement import MeasurementBase


class FileCollecting(MeasurementBase):
    def __init__(self, args, basedir=None, subdir=None):
        # init self.options and prepare self.outdir
        super(FileCollecting, self).__init__(args, basedir, subdir)
        # time when the object is created, used as a basement time point
        self.init_timepoint = time.time()

    # save_to_dir() saves srcfile to dstfile under self.oudir, if dstfile is not
    # specified, the filename of srcfile will remain unchanged
    def save_to_dir(self, srcfile=None, dstfile=None):
        if not srcfile:
            logging.debug("Source file unspecified, skipping.")
            return
        if not dstfile:
            shutil.copy(srcfile, self.outdir)
        else:
            shutil.copyfile(srcfile, os.path.join(self.outdir, dstfile))

    @abstractmethod
    def run_collecting(self):
        raise NotImplementedError
