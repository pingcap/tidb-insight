# -*- coding: utf-8 -*-
# Trace direct reclaim latency.

import os
import logging

from utils import util
from utils import fileopt
from utils.measurement import MeasurementBase


class DirectReclaimTracer(MeasurementBase):
    # tracefs mount point
    tracefs = "/sys/kernel/debug/tracing"
    direct_reclaim_begin = "events/vmscan/mm_vmscan_direct_reclaim_begin/enable"
    direct_reclaim_end = "events/vmscan/mm_vmscan_direct_reclaim_end/enable"

    def save_trace(self, cwd, outputdir=None):
        stderr = util.run_cmd(["cd", self.tracefs])[1]
        if stderr:
            logging.fatal("""ERROR: accessing tracing. Root user? Kernel has FTRACE?
            debugfs mounted? (mount -t debugfs debugfs /sys/kernel/debug)""")
            return

        if not outputdir:
            logging.fatal("ERROR: please give a dir to save trace data")
            return

        util.chdir(self.tracefs)

        # setup trace, set opt
        stderr = util.run_cmd(["echo nop > current_tracer"], shell=True)[1]
        if stderr:
            logging.fatal("ERROR: reset current_tracer failed")
            os.chdir(cwd)
            return

        bufsize_kb = self.options.bufsize if self.options.bufsize else 4096
        stderr = util.run_cmd(["echo %s > buffer_size_kb" %
                               bufsize_kb], shell=True)[1]
        if stderr:
            logging.fatal("ERROR: set bufsize_kb failed")
            os.chdir(cwd)
            return

        # begin tracing
        for event in [self.direct_reclaim_begin, self.direct_reclaim_end]:
            _, stderr = util.run_cmd(["echo 1 > %s" % event], shell=True)
            if stderr:
                logging.fatal("ERROR: enable %s tracepoint failed" % event)
                os.chdir(cwd)
                return

        # collect trace
        time = self.options.time if self.options.time else 60
        util.run_cmd_for_a_while(
            ["cat trace_pipe > %s/drtrace" % self.outdir], time, shell=True)

        # End tracing
        for event in [self.direct_reclaim_begin, self.direct_reclaim_end]:
            stderr = util.run_cmd(["echo 0 > %s" % event], shell=True)[1]
            if stderr:
                logging.fatal("ERROR: disable %s tracepoint failed" % event)
                os.chdir(cwd)
                return

        os.chdir(cwd)
