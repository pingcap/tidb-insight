# -*- coding: utf-8 -*-
# Collect stack trace with `perf`
#
# TODO: - switch to perf entire system or only given process(es)
#       - set time of perf record, default to 10s

import logging

from os import path

from utils import util
from utils import fileopt
from utils.measurement import MeasurementBase


class Perf(MeasurementBase):
    def __init__(self, args, basedir=None, subdir=None, process=None):
        # init self.options and prepare self.outdir
        super(Perf, self).__init__(args, basedir, subdir)

        # the process name and PID of processes(es) to run perf on,
        # perf entire system if empty, in format of {"PID": "name"}
        self.process_info = process if process else {}

    # set params of perf
    def build_record_cmd(self, pid=None, outfile=None):
        cmd = ["perf",    # default executable name
               "record",  # default action of perf
               "-g",
               "--call-graph",
               "dwarf"]

        cmd.append("-F")
        try:
            cmd.append("%d", self.options["freq"])
        except (KeyError, TypeError):
            cmd.append("120")  # default to 120Hz

        if pid:
            cmd.append("-p")
            cmd.append("%d" % pid)
        else:
            cmd.append("-a")  # default to whole system

        # default will be perf.data if neither pid nor outfile is specified
        if outfile:
            cmd.append("-o")
            cmd.append("%s/%s.data" % (self.outdir, outfile))
        elif not outfile and pid:
            cmd.append("-o")
            cmd.append("%s/%d.data" % (self.outdir, pid))

        cmd.append("sleep")
        try:
            cmd.append("%d", self.options["time"])
        except (KeyError, TypeError):
            cmd.append("10")  # default to 10s

        return cmd

    def build_archive_cmd(self, pid=None, outfile=None):
        cmd = ["perf",
               "archive"]

        # default will be perf.data if nothing specified
        if outfile:
            cmd.append("%s/%s.data" % (self.outdir, outfile))
        elif not outfile and pid:
            cmd.append("%s/%d.data" % (self.outdir, pid))
        else:
            cmd.append("%s/perf.data" % self.outdir)

        return cmd

    def run_collecting(self):
        if len(self.process_info) > 0:
            # perf on given process(es)
            for pid, pname in self.process_info.items():
                cmd = self.build_record_cmd(pid, pname)
                # TODO: unified output: "Now perf recording %s(%d)..." % (pname, pid)
                stdout, stderr = util.run_cmd(cmd)
                if stdout:
                    fileopt.write_file(
                        path.join(self.outdir, "%s.stdout" % pname), stdout)
                if stderr:
                    logging.warn(
                        "Command '%s' returned error: %s" % (cmd, stderr))
                if self.options.archive:
                    cmd = self.build_archive_cmd(pid, pname)
                    stdout, stderr = util.run_cmd(cmd)
                    if stderr:
                        logging.warn(
                            "Command '%s' returned error: %s" % (cmd, stderr))
        else:
            # perf the entire system
            cmd = self.build_record_cmd()
            stdout, stderr = util.run_cmd(cmd)
            if stdout:
                fileopt.write_file(
                    path.join(self.outdir, "perf.stdout"), stdout)
            if stderr:
                logging.warn("Command '%s' returned error: %s" % (cmd, stderr))
            if self.options.archive:
                cmd = self.build_archive_cmd()
                stdout, stderr = util.run_cmd(cmd)
                if stderr:
                    logging.warn(
                        "Command '%s' returned error: %s" % (cmd, stderr))
