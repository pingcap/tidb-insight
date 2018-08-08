# -*- coding: utf-8 -*-
# Get various config files

import logging
import os

from glob import glob

from file.base import FileCollecting
from utils import util
from utils import fileopt


class InsightConfigFiles(FileCollecting):
    def save_sysconf(self):
        cmd = ["sysctl", "-a"]
        path_limit_file = "/etc/security/limits.conf"

        # save limits.conf
        self.save_to_dir(srcfile=path_limit_file)

        # save `sysctl -a`
        stdout, stderr = util.run_cmd(cmd)
        if stdout:
            fileopt.write_file(os.path.join(
                self.outdir, "sysctl.conf"), stdout)
        if stderr:
            logging.warn("Reading limits.conf returned error: %s" % stderr)

    def find_tidb_configfiles(self, cmdline=None):
        cmd_opts = util.parse_cmdline(cmdline)
        # TODO: support relative path, this require `collector` to output cwd of process
        try:
            return cmd_opts["config"]
        except KeyError:
            return None

    def save_configs_auto(self, proc_cmdline=None):
        for pid, cmdline in proc_cmdline.items():
            proc_configfile = self.find_tidb_configfiles(cmdline)
            if not proc_configfile:
                continue
            self.save_to_dir(srcfile=proc_configfile, dstfile="%s-%s" %
                             (pid, proc_configfile.split('/')[-1]))

    def save_tidb_configs(self):
        def list_config_files(base_dir, prefix):
            file_list = []
            for file in os.listdir(base_dir):
                fullpath = os.path.join(base_dir, file)
                if os.path.isdir(fullpath):
                    # check for all sub-directories
                    file_list += list_config_files(fullpath, prefix)
                elif file.startswith(prefix):
                    file_list.append(fullpath)
            return file_list

        source_dir = self.options.dir
        if not source_dir or not os.path.isdir(source_dir):
            logging.fatal(
                "Source config path is not a directory. Did you set the correct `--config-dir`?")
            return
        file_prefix = self.options.prefix

        file_list = list_config_files(source_dir, file_prefix)
        for file in file_list:
            if self.options.alias in file:
                # Skip output files if source and output are the same directory
                continue
            self.save_to_dir(file)
            logging.info("Config file saved: %s" % file)

    def run_collecting(self, cmdline=None):
        if cmdline:
            self.save_configs_auto(cmdline)
        else:
            self.save_tidb_configs()
        if self.options.sysctl:
            self.save_sysconf()
