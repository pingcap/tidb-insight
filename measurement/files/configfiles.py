# -*- coding: utf-8 -*-
# Get various config files

import os
import shutil

from glob import glob

from measurement import util
from measurement.files import fileutils


class InsightConfigFiles():
    # options about logfiles
    config_options = {}

    # output dir
    config_dir = "conf"

    def __init__(self, options={}):
        self.config_options = options

    def save_sysconf(self, outputdir=None):
        cmd = ["sysctl", "-a"]
        path_limit_file = "/etc/security/limits.conf"

        # save output of `sysctl -a`
        full_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.config_dir)
        stdout, stderr = util.run_cmd(cmd)
        if stdout:
            fileutils.write_file(os.path.join(
                full_outputdir, "sysctl.conf"), stdout)
        if stderr:
            fileutils.write_file(os.path.join(
                full_outputdir, "sysctl.err"), stderr)

        # save system limits.conf
        shutil.copy(path_limit_file, full_outputdir)

    def find_tidb_configfiles(self, cmdline=""):
        cmd_opts = util.parse_cmdline(cmdline)
        # TODO: support relative path, this require `collector` to output cwd of process
        try:
            return cmd_opts["config"]
        except KeyError:
            return None
        return

    def save_tidb_configs(self, proc_cmdline=None, outputdir=None):
        full_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.config_dir)
        for pid, cmdline in proc_cmdline.items():
            proc_configfile = self.find_tidb_configfiles(cmdline)
            if not proc_configfile:
                continue
            shutil.copyfile(proc_configfile, os.path.join(
                full_outputdir, "%s.conf" % pid))
