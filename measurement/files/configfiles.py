# -*- coding: utf-8 -*-
# Get various config files

import logging
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

    def save_configs_auto(self, proc_cmdline=None, outputdir=None):
        full_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.config_dir)
        for pid, cmdline in proc_cmdline.items():
            proc_configfile = self.find_tidb_configfiles(cmdline)
            if not proc_configfile:
                continue
            shutil.copyfile(proc_configfile, os.path.join(
                full_outputdir, "%s.conf" % pid))

    def save_tidb_configs(self, outputdir=None):
        def list_config_files(base_dir, prefix):
            file_list = []
            for file in os.listdir(base_dir):
                fullpath = os.path.join(base_dir, file)
                if os.path.isdir(fullpath):
                    # check for all sub-directories
                    for f in list_config_files(fullpath, prefix):
                        file_list.append(f)
                if file.startswith(prefix):
                    file_list.append(fullpath)
            return file_list

        source_dir = self.config_options.config_dir
        if not source_dir or not os.path.isdir(source_dir):
            logging.fatal(
                "Source config path is not a directory. Did you set correct `--config-dir`?")
            return
        output_base = outputdir
        if not output_base:
            output_base = source_dir
        file_prefix = self.config_options.config_prefix

        # prepare output directory
        if not fileutils.create_dir(output_base):
            logging.fatal("Failed to prepare output dir.")
            return

        # the full path of output directory
        output_name = "%s_%s" % (file_prefix, self.config_options.alias)
        output_dir = os.path.join(output_base, output_name)

        file_list = list_config_files(source_dir, file_prefix)
        for file in file_list:
            if output_name in file:
                # Skip output files if source and output are the same directory
                continue
            shutil.copy(file, output_dir)
            logging.info("Config file saved: %s" % file)
