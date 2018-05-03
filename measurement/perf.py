# -*- coding: utf-8 -*-
# Collect stack trace with `perf`
#
# TODO: - switch to perf entire system or only given process(es)
#       - set time of perf record, default to 10s

from os import path
from subprocess import Popen, PIPE

from . import util

class InsightPerf():
    # the process name and PID of processes(es) to run perf on,
    # perf entire system if empty, in format of {"PID": "name"}
    process_info = {}

    # options of perfing
    perf_options = {}

    # default subdir name for perf data
    data_dir = "perfdata"

    def __init__(self, process={}, options={}):
        self.process_info = process
        self.perf_options = options

    # set params of perf
    def build_cmd(self, pid=None, outfile=None, outdir=None):
        cmd = ["perf",    # default executable name
                "record", # default action of perf
                "-g",
                "--call-graph",
                "dwarf"]
        try:
            # user defined path of perf
            cmd[0] = self.perf_options["perf_exec"]
        except (KeyError, TypeError):
            pass

        cmd.append("-F")
        try:
            cmd.append("%d", self.perf_options["perf_freq"])
        except (KeyError, TypeError):
            cmd.append("120") # default to 120Hz

        if pid != None:
            cmd.append("-p")
            cmd.append("%d" % pid)
        else:
            cmd.append("-a") # default to whole system

        if outfile != None:
            cmd.append("-o")
            cmd.append("%s/%s.data" % (outdir, outfile))
        elif outfile == None and pid != None:
            cmd.append("-o")
            cmd.append("%s/%d.data" % (outidr, pid))

        cmd.append("sleep")
        try:
            cmd.append("%d", self.perf_options["perf_time"])
        except (KeyError, TypeError):
            cmd.append("10") # default to 10s

        return cmd

    def run(self, outputdir=None):
        # set output path of perf data
        if outputdir == None:
            # default to current working dir
            outputdir = util.CheckDir(self.data_dir)
        elif outputdir[0] == '/':
            # absolute dir
            outputdir = util.CheckDir(path.join(outputdir, self.data_dir))
        else:
            # relative dir
            outputdir = util.CheckDir(path.join(util.cwd(), self.data_dir))

        if outputdir == None:
            # something went wrong when setting output dir, exit without perfing
            # TODO: unified output: "Error when setting up output dir of perf data"
            return

        if len(self.process_info) > 0:
            # perf on given process(es)
            for pid, pname in self.process_info.items():
                cmd = self.build_cmd(pid, pname, outputdir)
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                # TODO: unified output: "Now perf recording %s(%d)..." % (pname, pid)
                stdout, stderr = p.communicate()
                util.WriteFile(path.join(outputdir, "%s.stdout" % pname), stdout)
                if stderr != None:
                    util.WriteFile(path.join(outputdir, "%s.stderr" % pname), stderr)
        else:
            # perf the entire system
            cmd = self.build_cmd()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            # TODO: unified output: "Now perf recording..."
            stdout, stderr = p.communicate()
            util.WriteFile(path.join(outputdir, "perf.stdout"), stdout)
            if stderr != None:
                util.WriteFile(path.join(outputdir, "perf.stderr"), stderr)

def format_proc_info(proc_stats):
    result = {}
    for proc in proc_stats:
        result[proc["pid"]] = proc["name"]
    return result