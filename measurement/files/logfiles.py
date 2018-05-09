# -*- coding: utf-8 -*-
# Base class for logfile related stuff

import os
import shutil

from measurement import util

from measurement.files import fileutils


class InsightLogFiles():
    # options about logfiles
    log_options = {}

    # output dir
    log_dir = "logs"

    def __init__(self, options={}):
        self.log_options = options

    def find_tidb_logfiles(self, cmdline=""):
        cmd_opts = util.parse_cmdline(cmdline)
        # TODO: support relative path, this require `collector` to output cwd of process
        try:
            return cmd_opts["log-file"]
        except KeyError:
            return None

    def save_logfile_to_dir(self, logfile=None, savename=None, outputdir=None):
        if not logfile:
            return
        # set full output path for log files
        full_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.log_dir)
        if not savename:
            shutil.copy(logfile, full_outputdir)
        else:
            shutil.copyfile(logfile, os.path.join(full_outputdir, savename))

    def save_logfiles(self, proc_cmdline=None, outputdir=None):
        # save log files of TiDB modules
        for pid, cmdline in proc_cmdline.items():
            proc_logfile = self.find_tidb_logfiles(cmdline=cmdline)
            self.save_logfile_to_dir(logfile=proc_logfile,
                                     savename="log-%s.log" % pid,
                                     outputdir=outputdir)
