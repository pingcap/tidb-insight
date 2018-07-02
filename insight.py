#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 PingCAP, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This script is developed under Python 3.6 and compatiable with 3.2 and
# above, although Python 2 with version 2.7 and above may also work in
# most circumstances, please use latest Python 3 when possible.

import json
import logging
import os

from measurement import lsof
from measurement import perf
from measurement import space
from measurement import util
from measurement.files import configfiles
from measurement.files import fileutils
from measurement.files import logfiles
from measurement.process import meta as proc_meta
from measurement.tidb import pdctl
from measurement.ftrace import ftrace

class Insight():
    # data output dir
    outdir = "data"
    full_outdir = ""
    alias = ""

    insight_perf = None
    insight_logfiles = None
    insight_configfiles = None
    insight_pdctl = None
    insight_trace = None

    def __init__(self, args):
        if args.output:
            self.outdir = args.output
        if not args.alias:
            self.alias = util.get_hostname()
        self.full_outdir = fileutils.create_dir(
            os.path.join(self.outdir, self.alias))
        logging.debug("Output directory is: %s" % self.full_outdir)

    # data collected by `collector`
    collector_data = {}

    # parse process info in collector_data and build required dict
    def format_proc_info(self, keyname=None):
        if not keyname:
            return None
        result = {}
        for proc in self.collector_data["proc_stats"]:
            try:
                result[proc["pid"]] = proc[keyname]
            except KeyError:
                continue
        return result

    # collect data with `collector` and store it to disk
    def collector(self):
        # TODO: warn on non-empty output dir

        # call `collector` and store data to output dir
        base_dir = os.path.join(util.pwd(), "../")
        collector_exec = os.path.join(base_dir, "bin/collector")
        collector_outdir = fileutils.create_dir(
            os.path.join(self.full_outdir, "collector"))

        stdout, stderr = util.run_cmd(collector_exec)
        if stderr:
            logging.info("collector output:" % str(stderr))
        try:
            self.collector_data = json.loads(stdout)
        except json.JSONDecodeError:
            logging.critical("Error collecting system info:\n%s" % stderr)
            return

        # save various info to seperate .json files
        for k, v in self.collector_data.items():
            fileutils.write_file(os.path.join(collector_outdir, "%s.json" % k),
                                 json.dumps(v, indent=2))

    def run_perf(self, args):
        if not args.perf:
            logging.debug("Ignoring collecting of perf data.")
            return
        # perf requires root priviledge
        if not util.is_root_privilege():
            logging.fatal("It's required to run perf with root priviledge.")
            return

        # "--tidb-proc" has the highest priority
        if args.tidb_proc:
            # build dict of pid to process name
            perf_proc = self.format_proc_info("name")
            self.insight_perf = perf.InsightPerf(perf_proc, args)
        # parse pid list
        elif args.pid:
            perf_proc = {}
            for _pid in args.pid:
                perf_proc[_pid] = None
            self.insight_perf = perf.InsightPerf(perf_proc, args)
        # find process by port
        elif args.proc_listen_port:
            perf_proc = {}
            pid_list = proc_meta.find_process_by_port(
                args.proc_listen_port, args.proc_listen_proto)
            if not pid_list or len(pid_list) < 1:
                return
            for _pid in pid_list:
                perf_proc[_pid] = None
            self.insight_perf = perf.InsightPerf(perf_proc, args)
        else:
            self.insight_perf = perf.InsightPerf(options=args)
        self.insight_perf.run(self.full_outdir)

    def run_ftrace(self, args):
        if not args.ftrace:
            logging.debug("Ignoring collecting of ftrace data.")
            return
        # perf requires root priviledge
        if not util.is_root_privilege():
            logging.fatal("It's required to run ftrace with root priviledge.")
            return

        if args.ftracepoint:
            self.insight_ftrace = ftrace.InsightFtrace(args)
            self.insight_ftrace.run(self.full_outdir)
        else:
            logging.debug("Ignoring collecting of ftrace data, no tracepoint is chose.")


    def get_datadir_size(self):
        # du requires root priviledge to check data-dir
        if not util.is_root_privilege():
            logging.fatal(
                "It's required to check data-dir size with root priviledge.")
            return

        for proc in self.collector_data["proc_stats"]:
            args = util.parse_cmdline(proc["cmd"])
            try:
                data_dir = args["data-dir"]
            except KeyError:
                logging.debug(
                    "'data-dir' is not set in cmdline args: %s" % args)
                continue
            if os.listdir(data_dir) != []:
                stdout, stderr = space.du_subfiles(data_dir)
            else:
                stdout, stderr = space.du_total(data_dir)
            if stdout:
                fileutils.write_file(os.path.join(self.full_outdir, "size-%s" % proc["pid"]),
                                     stdout)
            if stderr:
                fileutils.write_file(os.path.join(self.full_outdir, "size-%s.err" % proc["pid"]),
                                     stderr)

    def get_lsof_tidb(self):
        # lsof requires root priviledge
        if not util.is_root_privilege():
            logging.fatal("It's required to run lsof with root priviledge.")
            return

        for proc in self.collector_data["proc_stats"]:
            stdout, stderr = lsof.lsof(proc["pid"])
            if stdout:
                fileutils.write_file(os.path.join(self.full_outdir, "lsof-%s") % proc["pid"],
                                     stdout)
            if stderr:
                fileutils.write_file(os.path.join(self.full_outdir, "lsof-%s.err" % proc["pid"]),
                                     stderr)

    def save_logfiles(self, args):
        if not args.log:
            logging.debug("Ignoring collecting of log files.")
            return
        # reading logs requires root priviledge
        if not util.is_root_privilege():
            logging.fatal("It's required to read logs with root priviledge.")
            return

        self.insight_logfiles = logfiles.InsightLogFiles(options=args)
        proc_cmdline = self.format_proc_info("cmd")  # cmdline of process
        if args.log_auto:
            self.insight_logfiles.save_logfiles_auto(
                proc_cmdline=proc_cmdline, outputdir=self.full_outdir)
        else:
            self.insight_logfiles.save_tidb_logfiles(
                outputdir=self.full_outdir)
        self.insight_logfiles.save_system_log(outputdir=self.full_outdir)

    def save_configs(self, args):
        if not args.config_file:
            logging.debug("Ignoring collecting of config files.")
            return

        self.insight_configfiles = configfiles.InsightConfigFiles(options=args)
        if args.config_sysctl:
            self.insight_configfiles.save_sysconf(outputdir=self.full_outdir)
        # collect TiDB configs
        if args.config_auto:
            proc_cmdline = self.format_proc_info("cmd")  # cmdline of process
            self.insight_configfiles.save_configs_auto(
                proc_cmdline=proc_cmdline, outputdir=self.full_outdir)
        else:
            self.insight_configfiles.save_tidb_configs(
                outputdir=self.full_outdir)

    def read_pdctl(self, args):
        self.insight_pdctl = pdctl.PDCtl(host=args.pd_host, port=args.pd_port)
        self.insight_pdctl.save_info(self.full_outdir)


if __name__ == "__main__":
    if not util.is_root_privilege():
        logging.warning("""Running TiDB Insight with non-superuser privilege may result
        in lack of some information or data in the final output, if
        you find certain data missing or empty in result, please try
        to run this script again with root.""")

    # WIP: add params to set output dir / overwriting on non-empty target dir
    args = util.parse_insight_opts()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Debug logging enabled.")

    insight = Insight(args)

    if (not args.pid and not args.proc_listen_port
        and not args.log_auto and not args.config_auto
        ):
        insight.collector()
        # check size of data folder of TiDB processes
        insight.get_datadir_size()
        # list files opened by TiDB processes
        insight.get_lsof_tidb()
    # WIP: call scripts that collect metrics of the node
    insight.run_perf(args)
    # save log files
    insight.save_logfiles(args)
    # save config files
    insight.save_configs(args)

    if args.pdctl:
        # read and save `pd-ctl` info
        insight.read_pdctl(args)

    # save ftrace data
    insight.run_ftrace(args)

    # compress all output to tarball
    if args.compress:
        fileutils.compress_tarball(insight.full_outdir, insight.alias)
