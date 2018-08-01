# -*- coding: utf-8 -*-

# Base Class for all file collecting features

import time

from abc import abstractmethod

from utils import util
from utils.measurement import MeasurementBase


class MetricBase(MeasurementBase):
    def __init__(self, args, basedir=None, subdir=None):
        # init self.options and prepare self.outdir
        super(MetricBase, self).__init__(args, basedir, subdir)
        # check timerange of metric data collecting
        self.end_time = util.parse_timestamp(
            args.end) if args.end else int(time.time())
        if args.retention:
            self.start_time = int(self.end_time - args.retention * 3600.0)
        else:
            # Default time period is 2 hours
            self.start_time = int(
                args.start if args.start else self.end_time - 7200.0)

    @abstractmethod
    def run_collecting(self):
        raise NotImplementedError
