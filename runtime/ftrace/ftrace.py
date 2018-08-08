# -*- coding: utf-8 -*-
# Collect stack trace with `ftrace`

import logging

from runtime.ftrace import drtracer
from utils import fileopt
from utils import util


class Ftrace(drtracer.DirectReclaimTracer):
    def __init__(self, args, basedir=None, subdir=None, cwd=None):
        # init self.options and prepare self.outdir
        super(Ftrace, self).__init__(args, basedir, subdir)
        self.cwd = cwd if cwd else util.cwd()

    def run_collecting(self):
        tracepoint = self.options.ftracepoint
        if tracepoint == "dr":
            self.save_trace(self.cwd, self.outdir)
        else:
            logging.debug("Tracepiont %s is not supported." % tracepoint)
