# -*- coding: utf-8 -*-
# Base class for logfile related stuff

import datetime
import logging
import os
import time

from glob import glob

from file.base import FileCollecting
from utils import util
from utils import fileopt


class InsightLogFiles(FileCollecting):
    def find_tidb_logfiles(self, cmdline=None):
        cmd_opts = util.parse_cmdline(cmdline)
        # TODO: support relative path, this require `collector` to output cwd of process
        try:
            return cmd_opts["log-file"]
        except KeyError:
            return None

    # check_time_range() checks if the comp_time is within a given range of time period
    # before base_time, it is used to filter only recent timepoints.
    def check_time_range(self, base_time=None, comp_time=None, valid_range=0):
        # Ingore time check if given valid_range is non-positive
        if valid_range <= 0:
            return True
        if not base_time:
            base_time = self.init_timepoint
        threhold = datetime.timedelta(0, 0, 0, 0, 0, valid_range)  # hour
        # we're checking for timepoints *before* base_time, so base_time's timestamp is greater.
        delta_secs = base_time - comp_time
        return datetime.timedelta(0, delta_secs) <= threhold

    def get_filelist_in_time(self, srcdir):
        valid_file_list = []
        if not os.path.isdir(srcdir):
            valid_file_list.append(srcdir)
            return valid_file_list
        for file in os.listdir(srcdir):
            fullpath = os.path.join(srcdir, file)
            if os.path.isdir(fullpath):
                # check for all sub-directories
                valid_file_list += self.get_filelist_in_time(fullpath)
            elif not self.check_time_range(comp_time=os.path.getmtime(fullpath),
                                           valid_range=self.options.retention):
                continue
            elif file.startswith(self.options.prefix):
                valid_file_list.append(fullpath)
        return valid_file_list

    def save_journal_log(self):
        journal_path = "/var/log/journal/*/*@*.journal"
        for logfile in glob(journal_path):
            if not self.check_time_range(comp_time=os.path.getmtime(logfile),
                                         valid_range=self.options.retention):
                continue
            self.save_to_dir(srcfile=logfile)

    def save_syslog(self):
        syslog_path = "/var/log/message*"
        dmesg_path = "/var/log/dmesg*"
        for logfile in glob(syslog_path) + glob(dmesg_path):
            if not self.check_time_range(comp_time=os.path.getmtime(logfile),
                                         valid_range=self.options.retention):
                continue
            self.save_to_dir(srcfile=logfile)

    def save_system_log(self):
        # save system logs
        if self.options.syslog:
            if util.get_init_type() == "systemd" and self.options.systemd:
                logging.info("systemd-journald detected.")
                self.save_journal_log()
            else:
                logging.info("systemd not detected, assuming syslog.")
            # always save syslogs
            self.save_syslog()

    def save_logfiles_auto(self, proc_cmdline=None):
        # save log files of TiDB modules
        for pid, cmdline in proc_cmdline.items():
            proc_logfile = self.find_tidb_logfiles(cmdline=cmdline)
            file_list = self.get_filelist_in_time(proc_logfile)
            for file in file_list:
                if self.options.alias in file:
                    # Skip output files if source and output are the same directory
                    continue
                self.save_to_dir(srcfile=file, dstfile="%s-%s" %
                                 (pid, file.split('/')[-1]))

    def save_tidb_logfiles(self):
        # init values of args
        source_dir = self.options.dir
        if not source_dir or not os.path.isdir(source_dir):
            logging.fatal(
                "Source log path is not a directory. Did you set correct `--log-dir`?")
            return

        # copy valid log files to output directory
        file_list = self.get_filelist_in_time(source_dir)
        for file in file_list:
            if self.options.alias in file:
                # Skip output files if source and output are the same directory
                continue
            self.save_to_dir(srcfile=file)
            logging.info("Logfile saved: %s", file)

    def run_collecting(self, cmdline=None):
        if cmdline:
            self.save_logfiles_auto(cmdline)
            self.save_system_log()
        elif self.options.syslog:
            self.save_system_log()
        else:
            self.save_tidb_logfiles()
