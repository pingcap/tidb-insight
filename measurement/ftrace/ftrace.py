# -*- coding: utf-8 -*-
# Collect stack trace with `ftrace`

from measurement.ftrace.mem import drtracer
from measurement.files import fileutils


class InsightFtrace():
    # options about tracer
    ftrace_options = {}
    cwd = ""

    # output dir
    data_dir = "ftracedata"

    def __init__(self, cwd, options):
        self.cwd = cwd
        self.ftrace_options = vars(options)

    def run(self, outputdir=None):
        ftrace_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.data_dir)

        if not ftrace_outputdir:
            return

        tracepoint = self.ftrace_options["ftracepoint"]
        if tracepoint == "dr":
            tracer = drtracer.DirectReclaimTracer(self.ftrace_options)
            tracer.save_trace(self.cwd, ftrace_outputdir)
        else:
            logging.debug("Tracepiont %s is not supported." % tracepoint)
