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


class Insight():
    # data output dir
    outdir = "data"
    full_outdir = ""

    def __init__(self, outdir=None):
        self.full_outdir = util.create_dir(self.outdir)

    # data collected by `collector`
    collector_data = {}
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
        util.write_file(os.path.join(self.full_outdir, "collector.json"),
                        json.dumps(self.collector_data, indent=2))

    def run_perf(self, args):
        if not args.perf:
            return

        # "--tidb-proc" has the highest priority
        if args.tidb_proc:
            perf_proc = perf.format_proc_info(
                self.collector_data["proc_stats"])
            insight_perf = perf.InsightPerf(perf_proc, args)
        # parse pid list
        elif len(args.pid) > 0:
            perf_proc = {}
            for _pid in args.pid:
                perf_proc[_pid] = None
            insight_perf = perf.InsightPerf(perf_proc, args)
        else:
            insight_perf = perf.InsightPerf(options=args)
        insight_perf.run(self.full_outdir)

    def get_datadir_size(self):
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
                util.write_file(os.path.join(self.full_outdir, "size-%s" % proc["pid"]),
                                stdout)
            if stderr:
                util.write_file(os.path.join(self.full_outdir, "size-%s.err" % proc["pid"]),
                                stderr)

    def get_lsof_tidb(self):
        for proc in self.collector_data["proc_stats"]:
            stdout, stderr = lsof.lsof(proc["pid"])
            if stdout:
                util.write_file(os.path.join(self.full_outdir, "lsof-%s") % proc["pid"],
                                stdout)
            if stderr:
                util.write_file(os.path.join(self.full_outdir, "lsof-%s.err" % proc["pid"]),
                                stderr)


if __name__ == "__main__":
    util.check_privilege()

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
