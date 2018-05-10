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


class Insight():
    # data output dir
    outdir = "data"
    full_outdir = ""

    insight_perf = None
    insight_logfiles = None
    insight_configfiles = None

    def __init__(self, outdir=None):
        self.full_outdir = fileutils.create_dir(self.outdir)

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
        # TODO: check existance of output dir
        # TODO: warn on non-empty output dir

        # call `collector` and store data to output dir
        base_dir = os.path.join(util.pwd(), "../")
        collector_exec = os.path.join(base_dir, "bin/collector")

        stdout, stderr = util.run_cmd(collector_exec)
        if stderr:
            logging.warning(str(stderr))
        try:
            self.collector_data = json.loads(stdout)
        except json.JSONDecodeError:
            # TODO: unified output: "Error collecting system info.\n%s" % stderr
            return
        fileutils.write_file(os.path.join(self.full_outdir, "collector.json"),
                             json.dumps(self.collector_data, indent=2))

    def run_perf(self, args):
        if not args.perf:
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
        elif len(args.pid) > 0:
            perf_proc = {}
            for _pid in args.pid:
                perf_proc[_pid] = None
            self.insight_perf = perf.InsightPerf(perf_proc, args)
        else:
            self.insight_perf = perf.InsightPerf(options=args)
        self.insight_perf.run(self.full_outdir)

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
            return
        # reading logs requires root priviledge
        if not util.is_root_privilege():
            logging.fatal("It's required to read logs with root priviledge.")
            return

        self.insight_logfiles = logfiles.InsightLogFiles(options=args)
        proc_cmdline = self.format_proc_info("cmd")  # cmdline of process
        self.insight_logfiles.save_logfiles(
            proc_cmdline=proc_cmdline, outputdir=self.outdir)

    def save_configs(self, args):
        if not args.config_file:
            return

        self.insight_configfiles = configfiles.InsightConfigFiles(options=args)
        self.insight_configfiles.save_sysctl(outputdir=self.outdir)


if __name__ == "__main__":
    if not util.is_root_privilege():
        logging.warning("""Running TiDB Insight with non-superuser privilege may result
        in lack of some information or data in the final output, if
        you find certain data missing or empty in result, please try
        to run this script again with root.""")

    # WIP: add params to set output dir / overwriting on non-empty target dir
    args = util.parse_insight_opts()
    insight = Insight()
    if args.output:
        insight.outdir = args.output

    insight.collector()
    # WIP: call scripts that collect metrics of the node
    insight.run_perf(args)
    # check size of data folder of TiDB processes
    insight.get_datadir_size()
    # list files opened by TiDB processes
    insight.get_lsof_tidb()
    # save log files
    insight.save_logfiles(args)
    # save config files
    insight.save_configs(args)
