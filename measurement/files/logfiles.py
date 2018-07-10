# -*- coding: utf-8 -*-
# Base class for logfile related stuff

import datetime
import logging
import os
import shutil
import time

from glob import glob

from measurement import util
from measurement.files import fileutils


class InsightLogFiles():
    # options about logfiles
    log_options = {}

    # output dir
    log_dir = "logs"

    # time when the object is created, used as a basement time point
    init_timepoint = None

    def __init__(self, options={}):
        self.log_options = options
        self.init_timepoint = time.time()

    def find_tidb_logfiles(self, cmdline=""):
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

    def get_filelist_in_time(self, base_dir, prefix, curr_time, retention_hour):
        valid_file_list = []
        for file in os.listdir(base_dir):
            fullpath = os.path.join(base_dir, file)
            if os.path.isdir(fullpath):
                # check for all sub-directories
                for f in self.get_filelist_in_time(fullpath, prefix, curr_time, retention_hour):
                    valid_file_list.append(f)
            if not self.check_time_range(curr_time, os.path.getmtime(fullpath), retention_hour):
                continue
            if file.startswith(prefix):
                valid_file_list.append(fullpath)
        return valid_file_list

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

    def save_journal_log(self, outputdir=None):
        journal_path = "/var/log/journal/*/*@*.journal"
        for logfile in glob(journal_path):
            self.save_logfile_to_dir(logfile=logfile, outputdir=outputdir)

    def save_syslog(self, outputdir=None):
        syslog_path = "/var/log/message*"
        dmesg_path = "/var/log/dmesg*"
        for logfile in glob(syslog_path) + glob(dmesg_path):
            self.save_logfile_to_dir(logfile=logfile, outputdir=outputdir)

    def save_logfiles_auto(self, proc_cmdline=None, outputdir=None):
        # save log files of TiDB modules
        for pid, cmdline in proc_cmdline.items():
            proc_logfile = self.find_tidb_logfiles(cmdline=cmdline)
            self.save_logfile_to_dir(logfile=proc_logfile,
                                     savename="%s.log" % pid,
                                     outputdir=outputdir)

    def save_system_log(self, outputdir=None):
        # save system logs
        if self.log_options.syslog:
            if util.get_init_type() == "systemd":
                logging.info("systemd-journald detected.")
                self.save_journal_log(outputdir=outputdir)
            else:
                logging.info("systemd not detected, assuming syslog.")
                self.save_syslog(outputdir=outputdir)

    def save_tidb_logfiles(self, outputdir=None):
        # init values of args
        source_dir = self.log_options.log_dir
        if not source_dir or not os.path.isdir(source_dir):
            logging.fatal(
                "Source log path is not a directory. Did you set correct `--log-dir`?")
            return
        output_base = outputdir
        if not output_base:
            output_base = source_dir
        file_prefix = self.log_options.log_prefix
        retention_hour = self.log_options.log_retention

        # prepare output directory
        if not fileutils.create_dir(output_base):
            logging.fatal("Failed to prepare output dir")
            return

        # the output tarball name
        output_name = "%s_%s" % (file_prefix, self.log_options.alias)
        # the full path of output directory
        output_dir = fileutils.build_full_output_dir(
            basedir=os.path.join(output_base, output_name), subdir=self.log_dir)

        # copy valid log files to output directory
        file_list = self.get_filelist_in_time(source_dir, file_prefix,
                                              time.time(), retention_hour)
        for file in file_list:
            if output_name in file:
                # Skip output files if source and output are the same directory
                continue
            shutil.copy(file, output_dir)
            logging.info("Logfile saved: %s", file)
