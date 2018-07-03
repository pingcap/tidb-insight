# -*- coding: utf-8 -*-
# Trace direct reclaim latency.

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
        _, stderr = util.run_cmd(["cd", tracefs])
        if stderr:
            logging.fatal("""ERROR: accessing tracing. Root user? Kernel has FTRACE?
            debugfs mounted? (mount -t debugfs debugfs /sys/kernel/debug)""")
            return

        # setup trace, set opt
        _, stderr = util.run_cmd(["echo", "nop", ">", "current_tracer"])
        if stderr:
            logging.fatal("ERROR: reset current_tracer failed")
            return

        bufsize_kb = self.ftrace_options["ftrace_bufsize_kb"] if "ftrace_bufsize_kb" in \
            self.ftrace_options and self.ftrace_options["ftrace_bufsize_kb"] else 4096
        _, stderr = util.run_cmd(["echo", bufsize_kb, ">", "buffer_size_kb"])
        if stderr:
            logging.fatal("ERROR: set bufsize_kb failed")
            return

        # begin tracing
        for event in [direct_reclaim_begin, direct_reclaim_end]:
            _, stderr = util.run_cmd(["echo", "1", ">", event])
            if stderr != "":
                logging.fatal("ERROR: enable %s tracepoint failed" % event)
                return

        # collect trace
        time = self.ftrace_options["ftrace_time"] if "ftrace_time" in \
            self.ftrace_options and self.ftrace_options["ftrace_time"] else 60
        full_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.data_dir)
        _, stderr = util.run_cmd(["cat", "trace_pipe", ">", full_outputdir], time)
        if stderr:
            logging.fatal("ERROR: set bufsize_kb failed")
            return

        # end tracing
        for event in [direct_reclaim_begin, direct_reclaim_end]:
            _, stderr = util.run_cmd(["echo", "0", ">", event])
            if stderr != "":
                logging.fatal("ERROR: disable %s tracepoint failed" % event)
                return
