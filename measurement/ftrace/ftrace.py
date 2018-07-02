# -*- coding: utf-8 -*-
# Collect stack trace with `ftrace`

from measurement.ftrace import mem


class InsightFtrace():
    # options about tracer
    ftrace_options = {}

    # output dir
    data_dir = "ftracedata"

    def __init__(self, options={}):
        self.ftrace_options = options

    def run(self, outputdir=None):
        ftrace_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.data_dir)

        if ftrace_outputdir is None:
            return

        tracepoint = self.ftrace_options["ftracepoint"]
        if tracepoint == "dr":
            tracer = mem.DirectReclaimTracer(self.ftrace_options)
            tracer.save_trace(ftrace_outputdir)
        else:
            logging.debug("Tracepiont %s is not supported." % tracepoint)
