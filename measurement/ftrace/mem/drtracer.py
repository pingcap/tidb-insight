# -*- coding: utf-8 -*-
# Trace direct reclaim latency.

import os
import logging

from measurement import util
from measurement.files import fileutils


class DirectReclaimTracer():
    # options about tracer
    ftrace_options = {}

    # output dir
    data_dir = "mem/drtrace"

    # tracefs mount point
    tracefs = "/sys/kernel/debug/tracing"
    direct_reclaim_begin = "events/vmscan/mm_vmscan_direct_reclaim_begin/enable"
    direct_reclaim_end = "events/vmscan/mm_vmscan_direct_reclaim_end/enable"

    def __init__(self, options={}):
        self.ftrace_options = options

    def save_trace(self, outputdir=None):
        _, stderr = util.run_cmd(["cd", self.tracefs])
        if stderr:
            logging.fatal("""ERROR: accessing tracing. Root user? Kernel has FTRACE?
            debugfs mounted? (mount -t debugfs debugfs /sys/kernel/debug)""")
            return

        os.chdir(self.tracefs)

        # setup trace, set opt
        _, stderr = util.run_cmd(["echo nop > current_tracer"], shell=True)
        if stderr:
            logging.fatal("ERROR: reset current_tracer failed")
            return

        bufsize_kb = self.ftrace_options["ftrace_bufsize_kb"] if "ftrace_bufsize_kb" in \
            self.ftrace_options and self.ftrace_options["ftrace_bufsize_kb"] else "4096"
        _, stderr = util.run_cmd(["echo %s > buffer_size_kb" % bufsize_kb], shell=True)
        if stderr:
            logging.fatal("ERROR: set bufsize_kb failed")
            return

        # begin tracing
        for event in [self.direct_reclaim_begin, self.direct_reclaim_end]:
            _, stderr = util.run_cmd(["echo 1 > %s" % event], shell=True)
            if stderr:
                logging.fatal("ERROR: enable %s tracepoint failed" % event)
                return

        # collect trace
        time = self.ftrace_options["ftrace_time"] if "ftrace_time" in \
            self.ftrace_options and self.ftrace_options["ftrace_time"] else 60
        full_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.data_dir)
        try:
            _, stderr = util.run_cmd(["cat", "trace_pipe", ">", full_outputdir], time)
            if stderr:
                logging.fatal("ERROR: redirect trace_pipe failed")
                return
        except:
            pass

        # End tracing
        for event in [self.direct_reclaim_begin, self.direct_reclaim_end]:
            _, stderr = util.run_cmd(["echo 0 > %s" % event], shell=True)
            if stderr:
                logging.fatal("ERROR: disable %s tracepoint failed" % event)
                return
