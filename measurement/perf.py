# -*- coding: utf-8 -*-
# Collect stack trace with `perf`
#
# TODO: - switch to perf entire system or only given process(es)
#       - set time of perf record, default to 10s

from os import path

from measurement import util
from measurement.files import fileutils


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
    def build_record_cmd(self, pid=None, outfile=None, outdir=None):
        cmd = ["perf",    # default executable name
               "record",  # default action of perf
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
            cmd.append("120")  # default to 120Hz

        if pid:
            cmd.append("-p")
            cmd.append("%d" % pid)
        else:
            cmd.append("-a")  # default to whole system

        # default will be perf.data if nothing specified
        if outfile:
            cmd.append("-o")
            cmd.append("%s/%s.data" % (outdir, outfile))
        elif not outfile and pid:
            cmd.append("-o")
            cmd.append("%s/%d.data" % (outdir, pid))

        cmd.append("sleep")
        try:
            cmd.append("%d", self.perf_options["perf_time"])
        except (KeyError, TypeError):
            cmd.append("10")  # default to 10s

        return cmd

    def build_archive_cmd(self, pid=None, outfile=None, outdir=None):
        cmd = ["perf",
               "archive"]

        # default will be perf.data if nothing specified
        if outfile:
            cmd.append("%s/%s.data" % (outdir, outfile))
        elif not outfile and pid:
            cmd.append("%s/%d.data" % (outdir, pid))
        else:
            cmd.append("%s/perf.data" % outdir)

        return cmd

    def run(self, outputdir=None):
        # set output path of perf data
        full_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.data_dir)

        if not full_outputdir:
            # something went wrong when setting output dir, exit without perfing
            # TODO: unified output: "Error when setting up output dir of perf data"
            return

        if len(self.process_info) > 0:
            # perf on given process(es)
            for pid, pname in self.process_info.items():
                cmd = self.build_record_cmd(pid, pname, full_outputdir)
                # TODO: unified output: "Now perf recording %s(%d)..." % (pname, pid)
                stdout, stderr = util.run_cmd(cmd)
                if stdout:
                    fileutils.write_file(
                        path.join(full_outputdir, "%s.stdout" % pname), stdout)
                if stderr:
                    fileutils.write_file(
                        path.join(full_outputdir, "%s.stderr" % pname), stderr)
                if self.perf_options.perf_archive:
                    cmd = self.build_archive_cmd(pid, pname, full_outputdir)
                    stdout, stderr = util.run_cmd(cmd)
                    if stderr:
                        fileutils.write_file(
                            path.join(full_outputdir, "%s.archive.stderr" % pname), stderr)
        else:
            # perf the entire system
            cmd = self.build_record_cmd()
            stdout, stderr = util.run_cmd(cmd)
            if stdout:
                fileutils.write_file(
                    path.join(full_outputdir, "perf.stdout"), stdout)
            if stderr:
                fileutils.write_file(
                    path.join(full_outputdir, "perf.stderr"), stderr)
            if self.perf_options.perf_archive:
                cmd = self.build_archive_cmd()
                stdout, stderr = util.run_cmd(cmd)
                if stderr:
                    fileutils.write_file(
                        path.join(full_outputdir, "perf.archive.stderr"), stderr)
